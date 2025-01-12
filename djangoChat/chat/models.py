from django.db import models
from django.db.models.signals import post_delete
from djangoChat.mysite import settings
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from djangoChat.mysite.json_extended import ExtendedDecoder, ExtendedEncoder

class Room(models.Model):
    # 채팅방 생성 유저를 저장할 수 있도록 외래키를 추가
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_room_set",
    )
    # 한글 채팅방 이름 필드로서 사용하려함
    # name 필드에서는 유일성 체크를 하지 않으므로
    # 같은 이름의 채팅방도 만들 수 있다.
    name = models.CharField(max_length=100)
        
    @property
    def chat_group_name(self) -> str:
        return self.make_chat_group_name(room=self)
    
    @classmethod
    def make_chat_group_name(cls, room=None, room_pk=None) -> str:
        return "chat-%s" % (room_pk or room.pk)
    
    class Meta:
    #쿼리셋 디폴트 정렬옵션 지정을 추천
        ordering = ["-pk"]
        
def room__on_post_delete(instance, **kwargs):
    # Consuemr Instance 밖에서 채팅방 그룹에 속한
    # 모든 Consumer Instances 들에게
    # chat.room.deleted 메세지를 보낸다.
    
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        instance.chat_group_name,
        {
            "type": "chat.room.deleted",
        }
    )
    
post_delete.connect(
    room__on_post_delete,
    sender=Room,
    dispatch_uid="room__on_post_delete"
)

class RoomMember(models.Model):
    room = models.ForeignKey("Room", on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)

    # 하나의 User가 하나의 Room에 대해, 다수의 접속이 있을 수 있음
    # 각 접속에서의 채널명 목록을 집합으로 저장하여, 최초접속 및 최종접속종료를 인지하도록 함
    # 디폴트로 빈 집합이 생성되도록 
    channel_names = models.JSONField(default=set,
                                     encoder=ExtendedEncoder,
                                     decoder=ExtendedDecoder,
                                     )