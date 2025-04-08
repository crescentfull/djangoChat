from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer
import logging

from chat.models import Room
from collections import defaultdict, deque


# 로거 설정
logger = logging.getLogger('chat')

# 메모리에 메시지를 저장(dict)
room_messages = defaultdict(lambda: deque(maxlen=5))
# JsonWebsocketConsumer를 상속받아 채팅 기능을 구현하는 클래스
class ChatConsumer(JsonWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.group_name = ""  # 웹소켓 그룹 이름을 저장
        self.room = None  # 현재 채팅방 객체를 저장
        logger.debug("ChatConsumer 인스턴스 생성")

    # 클라이언트가 웹소켓에 연결할 때 호출
    def connect(self):
        user = self.scope["user"]  # 현재 연결된 사용자를 가져옴
        logger.info(f"사용자 {user.username} 웹소켓 연결 시도")

        if not user.is_authenticated:
            logger.warning(f"인증되지 않은 사용자 연결 시도")
            self.close()  # 인증되지 않은 사용자는 연결을 닫음
        else:
            room_pk = self.scope["url_route"]["kwargs"]["room_pk"]  # URL에서 방의 기본 키를 가져옴
            logger.debug(f"채팅방 {room_pk} 연결 시도")

            try:
                self.room = Room.objects.get(pk=room_pk)  # 방 객체를 데이터베이스에서 가져옴
                logger.info(f"채팅방 {self.room.name} 연결 성공")
            except Room.DoesNotExist:
                logger.error(f"존재하지 않는 채팅방 {room_pk} 연결 시도")
                self.close()  # 방이 존재하지 않으면 연결을 닫음
            else:
                self.group_name = self.room.chat_group_name  # 방의 그룹 이름을 설정
                logger.debug(f"그룹 이름 설정: {self.group_name}")

                # 사용자가 방에 새로 참여했는지 확인
                is_new_join = self.room.user_join(self.channel_name, user)
                if is_new_join:
                    logger.info(f"사용자 {user.username}가 채팅방 {self.room.name}에 새로 참여")
                    # 메모리에 저장된 최근 메시지 전송
                    for message in room_messages[self.room.pk]:
                        self.send_json({
                            "type": "chat.message",
                            "message": message['content'],
                            "sender": message['sender'],
                        })
                    
                    # 새 사용자가 참여했음을 그룹에 알림
                    async_to_sync(self.channel_layer.group_send)(
                        self.group_name,
                        {
                            "type": "chat.user.join",
                            "username": user.username,
                        }
                    )
                else:
                    logger.debug(f"사용자 {user.username}가 이미 채팅방 {self.room.name}에 참여 중")

                # 사용자를 그룹에 추가
                async_to_sync(self.channel_layer.group_add)(
                    self.group_name,
                    self.channel_name,
                )

                self.accept()  # 연결을 수락
                logger.info(f"사용자 {user.username} 웹소켓 연결 수락")

    # 클라이언트가 웹소켓에서 연결을 끊을 때 호출
    def disconnect(self, code):
        user = self.scope["user"]
        logger.info(f"사용자 {user.username} 웹소켓 연결 종료 (코드: {code})")
        
        if self.group_name:
            # 사용자를 그룹에서 제거
            async_to_sync(self.channel_layer.group_discard)(
                self.group_name,
                self.channel_name,
            )
            logger.debug(f"사용자 {user.username}를 그룹 {self.group_name}에서 제거")

        if self.room is not None:
            # 사용자가 방을 마지막으로 떠나는지 확인
            is_last_leave = self.room.user_leave(self.channel_name, user)
            if is_last_leave:
                logger.info(f"사용자 {user.username}가 채팅방 {self.room.name}에서 마지막으로 퇴장")
                # 마지막 사용자가 떠났음을 그룹에 알림
                async_to_sync(self.channel_layer.group_send)(
                    self.group_name,
                    {
                        "type": "chat.user.leave",
                        "username": user.username,
                    }
                )
                # 채팅방에 남은 유저 수 확인, 0명이면 채팅방 삭제
                if self.room.get_online_users().count() == 0:
                    logger.info(f"채팅방 {self.room.name}에 사용자가 없어 삭제")
                    self.room.delete()

    # 클라이언트로부터 JSON 메시지를 받을 때 호출
    def receive_json(self, content, **kwargs):
        user = self.scope["user"]
        _type = content["type"]
        logger.debug(f"사용자 {user.username}로부터 메시지 수신: {_type}")

        if _type == "chat.message":
            sender = user.username
            message = content["message"]
            logger.info(f"사용자 {sender}가 메시지 전송: {message}")
            
            # 메시지를 그룹에 브로드캐스트
            async_to_sync(self.channel_layer.group_send)(
                self.group_name,
                {
                    "type": "chat.message",
                    "message": message,
                    "sender": sender,
                }
            )
        else:
            logger.warning(f"잘못된 메시지 타입: {_type}")

    # 그룹에서 'chat.user.join' 이벤트를 받을 때 호출
    def chat_user_join(self, message_dict):
        username = message_dict["username"]
        logger.debug(f"사용자 {username} 참여 이벤트 처리")
        self.send_json({
            "type": "chat.user.join",
            "username": username,
        })

    # 그룹에서 'chat.user.leave' 이벤트를 받을 때 호출
    def chat_user_leave(self, message_dict):
        username = message_dict["username"]
        logger.debug(f"사용자 {username} 퇴장 이벤트 처리")
        self.send_json({
            "type": "chat.user.leave",
            "username": username,
        })

    # 그룹에서 'chat.message' 이벤트를 받을 때 호출
    def chat_message(self, message_dict):
        logger.debug(f"메시지 이벤트 처리: {message_dict['sender']}: {message_dict['message']}")
        self.send_json({
            "type": "chat.message",
            "message": message_dict["message"],
            "sender": message_dict["sender"],
        })

    # 방이 삭제되었을 때 호출
    def chat_room_deleted(self, message_dict):
        logger.info(f"채팅방 삭제 이벤트 처리, 연결 종료")
        custom_code = 4000  # 사용자 정의 코드로 연결을 닫음
        self.close(code=custom_code)
