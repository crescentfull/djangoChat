from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from chat.forms import RoomForm
from chat.models import Room

def index(request: HttpRequest) -> HttpResponse:
    return render(request, "chat/index.html")

def room_new(request):
    if request.method == "POST":
        form = RoomForm(request.POST)
        if form.is_valid():
            created_room: Room = form.save()
            # room pk 기반으로 채팅방 URL을 만든다.
            return redirect("chat:room_chat", created_room.pk)
    else:
        form = RoomForm()
    
    return render(request, "chat/room_form.html", {
        "form": form,
    }) 
        
def room_chat(request: HttpRequest, room_name: str) -> HttpResponse:
    return render(request, "chat/room_chat.html", {
        "room_name": room_name,
    })
