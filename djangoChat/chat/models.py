from django.db import models
from django.db.models.signals import post_delete
from django.contrib.auth.models import User

from mysite import settings
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from mysite.json_extended import ExtendedDecoder, ExtendedEncoder

class OnlineUserMixin(models.Model):
    class Meta:
        abstract = True
    
    online_user_set = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        # 하나의 관계를 저장할 모델 지정
        through="RoomMember",
        # 모든 모델필드의 blank 디폴트값은 False
        blank=True,
        # user.joined_room_set.all() 코드로 user가 참여한 모든 Room 목록을 조회
        related_name="joined_room_set",
    )
    
    def get_online_users(self):
        """ 현 Room에 접속 중인 User 쿼리셋을 반환 """
        return self.online_user_set.all()
    
    def get_online_usernames(self):
        qs = self.get_online_users().values_list("username", flat=True)
        return list(qs)
    
    def is_joined_user(self, user):
        """ 지정 User가 현 Room의 접속 여부를 반환"""
        return self.get_online_users().filter(pk=user.pk).exists()
    
    def user_join(self, channel_name, user):
        """ 현 Room에 최초 접속여부를 반환 """
        try:
            room_member = RoomMember.objects.get(room=self, user=user)
        except RoomMember.DoesNotExist:
            room_member = RoomMember(room=self, user=user)

        is_new_join = len(room_member.channel_names) == 0
        room_member.channel_names.add(channel_name)
        
        if room_member.pk is None:
            room_member.save()
        else:
            room_member.save(update_fields=["channel_names"])
            
        return is_new_join
    
    def user_leave(self, channel_name, user):
        """ 현 Room으로부터 최종 접속종료 여부를 반환한다. """
        try:
            room_member = RoomMember.objects.get(room=self, user=user)
        except RoomMember.DoesNotExist:
            return True
        
        room_member.channel_names.remove(channel_name)
        if not room_member.channel_names:
            room_member.delete()
            return True
        else:
            room_member.save(update_fields=["channel_names"])
            return False
        
class Room(OnlineUserMixin,models.Model):
    # 채팅방 생성 유저를 저장할 수 있도록 외래키를 추가
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    # 한글 채팅방 이름 필드로서 사용하려함
    # name 필드에서는 유일성 체크를 하지 않으므로
    # 같은 이름의 채팅방도 만들 수 있다.
    name = models.CharField(max_length=255)
    description = models.TextField()
        
    class Meta:
        # 쿼리셋 디폴트 정렬옵션 지정을 추천
        ordering = ["-pk"]
        
    @property
    def chat_group_name(self):
        return self.make_chat_group_name(room=self)
    
    @staticmethod
    def make_chat_group_name(room=None, room_pk=None):
        return "chat-%s" % (room_pk or room.pk)
    
        
def room__on_post_delete(instance: Room, **kwargs):
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