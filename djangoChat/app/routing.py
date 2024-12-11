from django.urls import path
from app.consumers import EchoConsumer, LiveblogConsumer
from chat import consumers

websocket_urlpatterns = [
    path("ws/echo/", EchoConsumer.as_asgi()),
    path("ws/liveblog/", LiveblogConsumer.as_asgi()),
    path("ws/chat/<str:room_name>/chat/", consumers.ChatConsumer.as_asgi()),
]