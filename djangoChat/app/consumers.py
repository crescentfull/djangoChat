import json
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