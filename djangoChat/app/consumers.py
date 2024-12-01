import json
from channels.generic.websocket import WebsocketConsumer

# class EchoConsumer(WebsocketConsumer):
    
#     def receive(self, text_data=None, bytes_data=None):
#         obj = json.loads(text_data)
#         print("수신 :", obj)
#         json_string = json.dumps({
#             "content" : obj["content"],
#             "user" : obj["user"],
#         })
#         self.send(json_string)

class LiveblogConsumer(WebsocketConsumer):
    groups = ["liveblog"]
    
    # 그룹을 통해 받은 메세지 -> 웹소켓 클라 전달 (self.send(전달_메세지))
    # 메세지 type 값과 같은 이름의 메서드 호출
    
    # type "liveblog.post.created" => "liveblog_post_created" 메서드 호출 => 마침표(.)를 언더바(_)로 바꿈
    
    # 하나의 consumer에서 여러이벤트를 처리하다보며느 이벤트 type중복이 발생 가능. prefix 권장
    def liveblog_post_created(self, event_dict):
        self.send(json.dumps(event_dict))
    
    def liveblog_post_updated(self, event_dict):
        self.send(json.dumps(event_dict))
        
    def liveblog_post_deleted(self, event_dict):
        self.send(json.dumps(event_dict))