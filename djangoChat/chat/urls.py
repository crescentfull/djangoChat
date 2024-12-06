from django.urls import include, path
from chat import views

# URL Reverse 시의 namespace로서 활용
app_name = "chat"
urlpatterns = [
    path("", views.index, name="index"),
    path("<str:room_name>/chat/", views.room_chat, name="room_chat"),
]