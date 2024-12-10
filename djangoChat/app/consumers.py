import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer

class EchoConsumer(JsonWebsocketConsumer):
    
    def receive_json(self, content, **kwargs):
        print("수신 :", content)

        self.send_json({
            "content": content["content"],
            "user": content["user"],
        })

class LiveblogConsumer(JsonWebsocketConsumer):
    groups = ["liveblog"]
    
    # 그룹을 통해 받은 메세지 -> 웹소켓 클라 전달 (self.send(전달_메세지))
    # 메세지 type 값과 같은 이름의 메서드 호출
    
    # type "liveblog.post.created" => "liveblog_post_created" 메서드 호출 => 마침표(.)를 언더바(_)로 바꿈
    
    # 하나의 consumer에서 여러이벤트를 처리하다보며느 이벤트 type중복이 발생 가능. prefix 권장
    def liveblog_post_created(self, event_dict):
        self.send_json(event_dict)
    
    def liveblog_post_updated(self, event_dict):
        self.send_json(event_dict)
        
    def liveblog_post_deleted(self, event_dict):
        self.send_json(event_dict)
        
class ChatConsumer(JsonWebsocketConsumer):
    # room_name에 상관없이 모든 유저들을 광장(sqaure)을 통해 채팅
    SQUARE_GROUP_NAME = "square"
    groups = [SQUARE_GROUP_NAME]
    
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