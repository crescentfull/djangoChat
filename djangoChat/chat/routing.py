from django.urls import path
from chat import consumers

websocket_urlpatters = [
    path("ws/chat/<str:room_pk>/chat/", consumers.ChatConsumer.as_asgi()),
]