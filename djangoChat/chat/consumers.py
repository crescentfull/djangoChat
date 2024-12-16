from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer

class ChatConsumer(JsonWebsocketConsumer):
    # room_name에 상관없이 모든 유저들을 광장(sqaure)을 통해 채팅
    #SQUARE_GROUP_NAME = "square"
    #groups = [SQUARE_GROUP_NAME] 
    # 고정 그룹명 x , room_name에 기반하여 그룹명 생성
    
    def _init_(self):
        super().__init__()
        # 인스턴스 변수는 생성자 내에서 정의
        self.group_name = "" # 인스턴스 변수 group_name 추가
        
    def connect(self):
        # chat/routing.py 내 websocket_urlpatterns에 따라
        # /ws/chat/test/chat/ 요청의 경우 self.scope["url_route"] 값은?
        # => {'args':(), 'kwargs':{'room_name':'test'}}
        room_name = self.scope["url_route"]["kwargs"]["room_name"]
        
        # room_name에 기반하여 그룹명 생성
        self.group_name = f"chat-{room_name}"
        
        async_to_sync(self.channel_layer.group_add)(
            self.group_name,
            self.channel_name
        )
        
        # 본 웹소켓 접속을 허용
        # connect 메서드 기본 구현에서는 self.accept() 호출부만 존재
        self.accept()
    
    #단일 클라이언트로부터 메세지를 받으면 호출
    def receive_json(self, content, **kwargs):
        _type = content["type"]
        
        if _type == "chat.message":
            message = content["message"]
            # publish 과정: "square" 그룹 내 다른 Consumer를에게 메세지를 전달
            async_to_sync(self.channel_layer.group_send)(
                        {
                        "type": "chat.message",
                        "message": message,
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
        })