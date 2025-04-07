import pytest
from channels.testing import WebsocketCommunicator
from django.contrib.auth.models import User
from django.test import Client, TestCase
from asgiref.sync import sync_to_async
from django.urls import reverse
from channels.routing import URLRouter
from channels.auth import AuthMiddlewareStack
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer

from chat.routing import websocket_urlpatterns
from chat.models import Room, RoomMember
from chat.consumers import ChatConsumer


# 인메모리 채널 레이어를 사용하는 테스트용 애플리케이션 설정
@pytest.fixture
def test_app():
    return AuthMiddlewareStack(URLRouter(websocket_urlpatterns))


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_chat_consumer_connection(test_app):
    # 사용자와 채팅방 생성
    user = await database_sync_to_async(User.objects.create_user)(
        username='testuser', 
        password='password'
    )
    
    room = await database_sync_to_async(Room.objects.create)(
        name='Test Room', 
        owner=user
    )
    
    # 웹소켓 커뮤니케이터 생성
    communicator = WebsocketCommunicator(
        test_app, 
        f"/ws/chat/{room.pk}/chat/"
    )
    
    # 인증된 사용자 정보 추가
    communicator.scope["user"] = user
    
    # 연결 수행
    connected, _ = await communicator.connect()
    assert connected, "웹소켓 연결이 실패했습니다"

    # 연결 종료
    await communicator.disconnect()


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_chat_message_direct(test_app):
    """직접 소비자 인스턴스를 생성하여 테스트"""
    # 사용자와 채팅방 생성
    user = await database_sync_to_async(User.objects.create_user)(
        username='testuser', 
        password='password'
    )
    
    room = await database_sync_to_async(Room.objects.create)(
        name='Test Room', 
        owner=user
    )
    
    # 웹소켓 스코프 생성
    scope = {
        "type": "websocket",
        "url_route": {"kwargs": {"room_pk": str(room.pk)}},
        "user": user,
    }
    
    # 소비자 인스턴스 직접 생성
    # JsonWebsocketConsumer의 초기화를 위해 필요한 속성 설정
    from channels.generic.websocket import JsonWebsocketConsumer
    from channels.testing import WebsocketCommunicator
    
    # 테스트용 웹소켓 커뮤니케이터 생성
    communicator = WebsocketCommunicator(
        test_app, 
        f"/ws/chat/{room.pk}/chat/"
    )
    
    # 인증된 사용자 정보 추가
    communicator.scope["user"] = user
    
    # 연결 수행
    connected, _ = await communicator.connect()
    assert connected, "웹소켓 연결이 실패했습니다"
    
    # 메시지 전송 테스트
    await communicator.send_json_to({
        "type": "chat.message",
        "message": "테스트 메시지"
    })
    
    # 응답 확인
    response = await communicator.receive_json_from()
    assert response["type"] == "chat.message", "응답 타입이 chat.message가 아닙니다"
    assert response["message"] == "테스트 메시지", "메시지 내용이 일치하지 않습니다"
    
    # 연결 종료
    await communicator.disconnect()


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_chat_room_model():
    """Room 모델의 메서드를 직접 테스트"""
    # 사용자와 채팅방 생성
    user1 = await database_sync_to_async(User.objects.create_user)(
        username='user1', 
        password='password1'
    )
    
    user2 = await database_sync_to_async(User.objects.create_user)(
        username='user2', 
        password='password2'
    )
    
    room = await database_sync_to_async(Room.objects.create)(
        name='Test Room', 
        owner=user1
    )
    
    # 채널 이름 생성
    channel_name1 = "test_channel_1"
    channel_name2 = "test_channel_2"
    
    # 사용자 참여 테스트
    is_new_join1 = await database_sync_to_async(room.user_join)(channel_name1, user1)
    assert is_new_join1, "첫 번째 사용자 참여가 새로운 참여로 등록되어야 합니다"
    
    is_new_join2 = await database_sync_to_async(room.user_join)(channel_name2, user2)
    assert is_new_join2, "두 번째 사용자 참여가 새로운 참여로 등록되어야 합니다"
    
    # 온라인 사용자 확인
    online_users = await database_sync_to_async(lambda: list(room.get_online_users()))()
    assert len(online_users) == 2, "온라인 사용자 수가 2명이어야 합니다"
    
    # 사용자 퇴장 테스트
    is_last_leave1 = await database_sync_to_async(room.user_leave)(channel_name1, user1)
    assert is_last_leave1, "사용자 1의 마지막 채널이므로 True를 반환해야 합니다"
    
    is_last_leave2 = await database_sync_to_async(room.user_leave)(channel_name2, user2)
    assert is_last_leave2, "사용자 2의 마지막 채널이므로 True를 반환해야 합니다"
    
    # 모든 사용자가 나간 후 확인
    online_users = await database_sync_to_async(lambda: list(room.get_online_users()))()
    assert len(online_users) == 0, "모든 사용자가 퇴장한 후에는 온라인 사용자가 없어야 합니다"


class ChatModelTests(TestCase):
    """채팅 모델 관련 기능 테스트"""
    
    def setUp(self):
        # 테스트용 사용자 생성
        self.user1 = User.objects.create_user(username='user1', password='password1')
        self.user2 = User.objects.create_user(username='user2', password='password2')
        
        # 테스트용 채팅방 생성
        self.room = Room.objects.create(name='Test Room', owner=self.user1)
    
    def test_room_creation(self):
        """채팅방 생성 테스트"""
        self.assertEqual(self.room.name, 'Test Room')
        self.assertEqual(self.room.owner, self.user1)
        self.assertEqual(self.room.get_online_users().count(), 0)
    
    def test_room_user_join_leave(self):
        """사용자 참여 및 퇴장 테스트"""
        # 사용자 1 참여
        is_new_join1 = self.room.user_join("channel1", self.user1)
        self.assertTrue(is_new_join1)
        self.assertEqual(self.room.get_online_users().count(), 1)
        
        # 같은 사용자가 다른 채널로 재참여 (새 세션)
        is_new_join1_again = self.room.user_join("channel2", self.user1)
        self.assertFalse(is_new_join1_again)  # 이미 참여한 사용자라 새 참여는 아님
        
        # 사용자 2 참여
        is_new_join2 = self.room.user_join("channel3", self.user2)
        self.assertTrue(is_new_join2)
        self.assertEqual(self.room.get_online_users().count(), 2)
        
        # 사용자 1의 첫 번째 채널 퇴장
        is_last_leave1 = self.room.user_leave("channel1", self.user1)
        self.assertFalse(is_last_leave1)  # 아직 채널2로 접속 중이므로 마지막 퇴장은 아님
        
        # 사용자 1의 모든 채널 퇴장
        is_last_leave1_final = self.room.user_leave("channel2", self.user1)
        self.assertTrue(is_last_leave1_final)  # 사용자 1의 마지막 채널이 제거됨
        
        # 사용자 2 퇴장
        is_last_leave2 = self.room.user_leave("channel3", self.user2)
        self.assertTrue(is_last_leave2)  # 마지막 사용자 퇴장
        
        # 모든 사용자가 나간 후 확인
        self.assertEqual(self.room.get_online_users().count(), 0)
    
    def test_room_online_users(self):
        """온라인 사용자 목록 테스트"""
        # 사용자 참여 전 확인
        self.assertEqual(len(self.room.get_online_usernames()), 0)
        
        # 사용자 참여
        self.room.user_join("channel1", self.user1)
        self.room.user_join("channel2", self.user2)
        
        # 온라인 사용자 목록 확인
        usernames = self.room.get_online_usernames()
        self.assertEqual(len(usernames), 2)
        self.assertIn('user1', usernames)
        self.assertIn('user2', usernames)
        
        # 사용자 1 퇴장 후 확인
        self.room.user_leave("channel1", self.user1)
        usernames = self.room.get_online_usernames()
        self.assertEqual(len(usernames), 1)
        self.assertIn('user2', usernames)
        self.assertNotIn('user1', usernames)


class ChatViewTests(TestCase):
    """채팅 뷰 기능 테스트"""
    
    def setUp(self):
        # 테스트용 사용자 생성
        self.user = User.objects.create_user(username='testuser', password='password')
        
        # 클라이언트 설정
        self.client = Client()
        self.client.login(username='testuser', password='password')
        
        # 테스트용 채팅방 생성
        self.room = Room.objects.create(name='Test Room', owner=self.user)
    
    def test_index_view(self):
        """메인 페이지 테스트"""
        response = self.client.get(reverse('chat:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'chat/index.html')
        self.assertContains(response, 'Test Room')
    
    def test_room_new_view(self):
        """새 채팅방 생성 테스트"""
        # GET 요청 테스트
        response = self.client.get(reverse('chat:room_new'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'chat/room_form.html')
        
        # POST 요청으로 새 채팅방 생성
        response = self.client.post(
            reverse('chat:room_new'), 
            {'name': 'New Test Room'}
        )
        self.assertEqual(response.status_code, 302)  # 리다이렉트
        
        # 새 채팅방이 생성되었는지 확인
        self.assertTrue(Room.objects.filter(name='New Test Room').exists())
    
    def test_room_chat_view(self):
        """채팅방 페이지 테스트"""
        response = self.client.get(
            reverse('chat:room_chat', args=[self.room.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'chat/room_chat.html')
        self.assertContains(response, self.room.name)
    
    def test_room_delete_view(self):
        """채팅방 삭제 테스트"""
        # GET 요청 테스트
        response = self.client.get(
            reverse('chat:room_delete', args=[self.room.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'chat/room_confirm_delete.html')
        
        # POST 요청으로 채팅방 삭제
        response = self.client.post(
            reverse('chat:room_delete', args=[self.room.pk])
        )
        self.assertEqual(response.status_code, 302)  # 리다이렉트
        
        # 채팅방이 삭제되었는지 확인
        self.assertFalse(Room.objects.filter(pk=self.room.pk).exists())
    
    def test_room_users_view(self):
        """방 사용자 목록 API 테스트"""
        # 먼저 사용자 참여
        self.room.user_join("test_channel", self.user)
        
        # API 호출
        response = self.client.get(
            reverse('chat:room_users', args=[self.room.pk])
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode(),
            {'username_list': ['testuser']}
        )


class RoomMemberTests(TestCase):
    """RoomMember 모델 테스트"""
    
    def setUp(self):
        # 테스트용 사용자 생성
        self.user = User.objects.create_user(username='testuser', password='password')
        
        # 테스트용 채팅방 생성
        self.room = Room.objects.create(name='Test Room', owner=self.user)
    
    def test_channel_names_field(self):
        """channel_names 필드 동작 테스트"""
        # RoomMember 생성
        room_member = RoomMember.objects.create(
            room=self.room,
            user=self.user,
        )
        
        # 채널 추가 및 저장
        room_member.channel_names.add("channel1")
        room_member.save()
        
        # 데이터베이스에서 다시 불러와서 확인
        refreshed_member = RoomMember.objects.get(pk=room_member.pk)
        self.assertIn("channel1", refreshed_member.channel_names)
        
        # 채널 추가 및 저장
        refreshed_member.channel_names.add("channel2")
        refreshed_member.save()
        
        # 다시 불러와서 확인
        refreshed_member = RoomMember.objects.get(pk=room_member.pk)
        self.assertIn("channel1", refreshed_member.channel_names)
        self.assertIn("channel2", refreshed_member.channel_names)
        self.assertEqual(len(refreshed_member.channel_names), 2)
        
        # 채널 제거 및 저장
        refreshed_member.channel_names.remove("channel1")
        refreshed_member.save()
        
        # 다시 불러와서 확인
        refreshed_member = RoomMember.objects.get(pk=room_member.pk)
        self.assertNotIn("channel1", refreshed_member.channel_names)
        self.assertIn("channel2", refreshed_member.channel_names)
        self.assertEqual(len(refreshed_member.channel_names), 1)