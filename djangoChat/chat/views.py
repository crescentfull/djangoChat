from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

def index(request: HttpRequest) -> HttpResponse:
    return render(request, "chat/index.html")

def room_chat(request: HttpRequest, room_name: str) -> HttpResponse:
    return render(request, "chat/room_chat.html", {
        "room_name": room_name,
    })