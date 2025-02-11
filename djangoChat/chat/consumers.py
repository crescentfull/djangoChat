from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer

from chat.models import Room

# JsonWebsocketConsumer를 상속받아 채팅 기능을 구현하는 클래스
class ChatConsumer(JsonWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.group_name = ""  # 웹소켓 그룹 이름을 저장
        self.room = None  # 현재 채팅방 객체를 저장

    # 클라이언트가 웹소켓에 연결할 때 호출
    def connect(self):
        user = self.scope["user"]  # 현재 연결된 사용자를 가져옴

        if not user.is_authenticated:
            self.close()  # 인증되지 않은 사용자는 연결을 닫음
        else:
            room_pk = self.scope["url_route"]["kwargs"]["room_pk"]  # URL에서 방의 기본 키를 가져옴

            try:
                self.room = Room.objects.get(pk=room_pk)  # 방 객체를 데이터베이스에서 가져옴
            except Room.DoesNotExist:
                self.close()  # 방이 존재하지 않으면 연결을 닫음
            else:
                self.group_name = self.room.chat_group_name  # 방의 그룹 이름을 설정

                # 사용자가 방에 새로 참여했는지 확인
                is_new_join = self.room.user_join(self.channel_name, user)
                if is_new_join:
                    # 새 사용자가 참여했음을 그룹에 알림
                    async_to_sync(self.channel_layer.group_send)(
                        self.group_name,
                        {
                            "type": "chat.user.join",
                            "username": user.username,
                        }
                    )

                # 사용자를 그룹에 추가
                async_to_sync(self.channel_layer.group_add)(
                    self.group_name,
                    self.channel_name,
                )

                self.accept()  # 연결을 수락

    # 클라이언트가 웹소켓에서 연결을 끊을 때 호출
    def disconnect(self, code):
        if self.group_name:
            # 사용자를 그룹에서 제거
            async_to_sync(self.channel_layer.group_discard)(
                self.group_name,
                self.channel_name,
            )

        user = self.scope["user"]

        if self.room is not None:
            # 사용자가 방을 마지막으로 떠나는지 확인
            is_last_leave = self.room.user_leave(self.channel_name, user)
            if is_last_leave:
                # 마지막 사용자가 떠났음을 그룹에 알림
                async_to_sync(self.channel_layer.group_send)(
                    self.group_name,
                    {
                        "type": "chat.user.leave",
                        "username": user.username,
                    }
                )

    # 클라이언트로부터 JSON 메시지를 받을 때 호출
    def receive_json(self, content, **kwargs):
        user = self.scope["user"]

        _type = content["type"]

        if _type == "chat.message":
            sender = user.username
            message = content["message"]
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
            print(f"Invalid message type : ${_type}")

    # 그룹에서 'chat.user.join' 이벤트를 받을 때 호출
    def chat_user_join(self, message_dict):
        self.send_json({
            "type": "chat.user.join",
            "username": message_dict["username"],
        })

    # 그룹에서 'chat.user.leave' 이벤트를 받을 때 호출
    def chat_user_leave(self, message_dict):
        self.send_json({
            "type": "chat.user.leave",
            "username": message_dict["username"],
        })

    # 그룹에서 'chat.message' 이벤트를 받을 때 호출
    def chat_message(self, message_dict):
        self.send_json({
            "type": "chat.message",
            "message": message_dict["message"],
            "sender": message_dict["sender"],
        })

    # 방이 삭제되었을 때 호출
    def chat_room_deleted(self, message_dict):
        custom_code = 4000  # 사용자 정의 코드로 연결을 닫음
        self.close(code=custom_code)
