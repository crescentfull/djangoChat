from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer
from chat.models import Room

class ChatConsumer(JsonWebsocketConsumer):
    # room_name에 상관없이 모든 유저들을 광장(sqaure)을 통해 채팅
    #SQUARE_GROUP_NAME = "square"
    #groups = [SQUARE_GROUP_NAME] 
    # 고정 그룹명 x , room_name에 기반하여 그룹명 생성
    
    def _init_(self):
        super().__init__()
        # 파이썬 클래스에서 인스턴스 변수는 생성자 내에서 정의
        self.group_name = "" # 인스턴스 변수 group_name 추가
        
    def connect(self):
        # asgi.py에서 AuthMiddlewareStack을 적용하지 않았다면 KeyError 발생
        # AnonymousUser 인스턴스 혹은 User 인스턴스
        user = self.scope["user"]
        
        if not user.is_authenticated:
            #인증되지 않은 웹소켓 접속 거부
            #room_chat 뷰에서 인증상태에서만 렌더링됨, 인증되지 않은 웹소켓 요청은 있을 수 없다.
            #connect에서의 self.close() 호출은 종료코드 1006(비정상 종료)으로 강제전달,
            #다른 메서드에서의 self.close() 호출은 디폴트로 종료코드 1000(정상 종료)으로 전달됨
            #웹프론트엔드 웹소켓 onclose 핸들러에서 event.code 속성으로 종료코드 참조
            self.close()
        else:
            room_pk = self.scope["url_route"]["kwargs"]["room_pk"]
            self.group_name = Room.make_chat_group_name(room_pk=room_pk)   
            
            async_to_sync(self.channel_layer.group_add)(
                self.group_name, self.channel_name
            )
            self.accept()
            
    # 웹 소켓 클라이언트와 접속이 끊어졌을 때, 호출됨
    def disconnect(self, code):
        if self.group_name:
            async_to_sync(self.channel_layer.group_discard)(
                self.group_name, self.channel_name
            )
    
    #단일 클라이언트로부터 메세지를 받으면 호출
    def receive_json(self, content, **kwargs):
        user = self.scope["user"]
        
        _type = content["type"]
        
        if _type == "chat.message":
            message = content["message"]
            sender = user.username
            # publish 과정: "square" 그룹 내 다른 Consumer를에게 메세지를 전달
            async_to_sync(self.channel_layer.group_send)(
                        self.group_name,
                        {
                        "type": "chat.message",
                        "message": message,
                        "sender": sender,
                    },
                )
        else:
            print(f"Invalid message type : {_type}")
    
    # 그룹을 통해 type="chat.message"메세지를 받으면 호출됨
    def chat_message(self, message_dict):
        # 접속되어 있는 클라이언트에게 메세지를 전달한다
        # 클라이언트에게 전달하는 값들을 명시적으로 지정
        # 원하는 포맷으로 메세지를 구성
        self.send_json({
            "type": "chat.message",
            "message": message_dict["message"],
            "sender": message_dict["sender"]
        })
    
    
    # 채팅방이 삭제되면 호출됨
    # 웹소켓 클라이언트로 메세지를 전달하여 클라이언트에 의해 웹소켓 연결을 끊도록 함
    def chat_room_deleted(self, message_dict):
        self.send_json({
            "type": "chat.room.deleted",
        })