from django.urls import include, path
from chat import views

# URL Reverse 시의 namespace로서 활용
app_name = "chat"
urlpatterns = [
    path("", views.index, name="index"),
    path("<str:room_pk>/chat/", views.room_chat, name="room_chat"), # room_name => room_pk
    path("new/", views.room_new, name="room_new"),
    path("<int:room_pk>/delete/", views.room_delete, name="room_delete"),
    path("<int:room_pk>/users", views.room_users, name="room_users"),
]