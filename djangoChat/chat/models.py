from django.db import models
from django.db.models.signals import post_delete
from djangoChat.mysite import settings
from channels.layers import get_channel_layer

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