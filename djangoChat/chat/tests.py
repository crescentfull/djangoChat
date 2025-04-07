import pytest
from channels.testing import WebsocketCommunicator
from django.contrib.auth.models import User
from django.test import Client
from chat.routing import websocket_urlpatterns  # 실제 경로로 변경하세요
from chat.models import Room

@pytest.mark.django_db
@pytest.mark.asyncio
async def test_chat_websocket():
    # 테스트용 사용자 생성
    user = User.objects.create_user(username='testuser', password='password')
    
    # 테스트용 채팅방 생성
    room = Room.objects.create(name='Test Room', owner=user)

    # Django 테스트 클라이언트를 사용하여 로그인
    client = Client()
    client.login(username='testuser', password='password')

    # WebSocketCommunicator를 사용하여 WebSocket 연결 시뮬레이션
    communicator = WebsocketCommunicator(websocket_urlpatterns, f"/ws/chat/{room.pk}/")
    connected, _ = await communicator.connect()
    assert connected

    # 메시지 전송 테스트
    await communicator.send_json_to({
        "type": "chat.message",
        "message": "Hello, world!"
    })

    response = await communicator.receive_json_from()
    assert response["type"] == "chat.message"
    assert response["message"] == "Hello, world!"

    # WebSocket 연결 종료
    await communicator.disconnect()