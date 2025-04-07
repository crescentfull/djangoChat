from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from django.db import models
from django.db.models.signals import post_delete
from django.contrib.auth.models import User
import logging

from mysite.json_extended import ExtendedJSONEncoder, ExtendedJSONDecoder

logger = logging.getLogger('chat')


# 온라인 사용자 관리를 위한 믹스인 클래스
class OnlineUserMixin(models.Model):
    class Meta:
        abstract = True # 추상 모델로 정의

    online_user_set = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="RoomMember",
        blank=True,
        related_name="joined_room_set",
    )

    # 현재 온라인 사용자 목록을 반환하는 메서드
    def get_online_users(self):
        return self.online_user_set.all()

    # 온라인 사용자의 사용자 이름 목록을 반환하는 메서드
    def get_online_usernames(self):
        qs = self.get_online_users().values_list("username", flat=True)
        return list(qs)

    # 사용자가 방에 참여했는지 확인하는 메서드
    def is_joined_user(self, user):
        return self.get_online_users().filter(pk=user.pk).exists()

    def user_join(self, channel_name, user):
        logger.debug(f"사용자 {user.username}가 채팅방 {self.name}에 참여 시도")
        try:
            room_member = RoomMember.objects.get(room=self, user=user)
        except RoomMember.DoesNotExist:
            room_member = RoomMember(room=self, user=user)

        # 새로운 사용자가 참여한 경우
        is_new_join = len(room_member.channel_names) == 0
        room_member.channel_names.add(channel_name)

        if room_member.pk is None:
            room_member.save()
        else:
            room_member.save(update_fields=["channel_names"])

        logger.info(f"사용자 {user.username}가 채팅방 {self.name}에 참여")
        return is_new_join

    def user_leave(self, channel_name, user):
        logger.debug(f"사용자 {user.username}가 채팅방 {self.name}에서 퇴장 시도")
        try:
            room_member = RoomMember.objects.get(room=self, user=user)
        except RoomMember.DoesNotExist:
            return True

        room_member.channel_names.remove(channel_name)
        if not room_member.channel_names:
            room_member.delete()
            logger.info(f"사용자 {user.username}가 채팅방 {self.name}에서 퇴장")
            return True
        else:
            room_member.save(update_fields=["channel_names"])
            logger.debug(f"사용자 {user.username}가 채팅방 {self.name}에 없음")
            return False


class Room(OnlineUserMixin, models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_room_set",
    )
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    users = models.ManyToManyField(User, related_name='chat_rooms')
    online_users = models.ManyToManyField(User, related_name='online_rooms', blank=True)
    channel_names = models.JSONField(default=dict)

    class Meta:
        ordering = ["-pk"] # 방 목록을 내림차순으로 정렬

    @property
    def chat_group_name(self):
        return self.make_chat_group_name(room=self)

    @staticmethod
    def make_chat_group_name(room=None, room_pk=None):
        return "chat-%s" % (room_pk or room.pk)

    def __str__(self):
        return self.name


def room__on_post_delete(instance: Room, **kwargs):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        instance.chat_group_name,
        {
            "type": "chat.room.deleted",
        }
    )

# post_delete 시그널을 연결하여 Room 모델이 삭제될 때 호출되도록 함
post_delete.connect(
    room__on_post_delete,
    sender=Room,
    dispatch_uid="room__on_post_delete",
)


class RoomMember(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    channel_names = models.JSONField(
        default=set,
        encoder=ExtendedJSONEncoder,
        decoder=ExtendedJSONDecoder,
    )