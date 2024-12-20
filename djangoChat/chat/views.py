from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render, get_object_or_404

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
        
def room_chat(request: HttpRequest, room_pk: str) -> HttpResponse:
    room = get_object_or_404(Room, pk=room_pk)
    return render(request, "chat/room_chat.html", {
        "room": room,
    })
