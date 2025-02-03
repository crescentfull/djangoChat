
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render, get_object_or_404, resolve_url
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import CreateView

from chat.forms import RoomForm
from chat.models import Room

def index(request):
    #.order_by("-pk")를 지정하지 않으면,
    # room 모델의 디폴트 정렬 옵션이 지정된다.
    room_qs = Room.objects.all()
    
    return render(request, "chat/index.html", {
        "room_list" : room_qs,
    })

@login_required
def room_new(request):
    if request.method == "POST":
        form = RoomForm(request.POST)
        if form.is_valid():
            created_room: Room = form.save(commit=False)
            created_room.owner =  request.user
            created_room.save()
            # room pk 기반으로 채팅방 URL을 만든다.
            return redirect("chat:room_chat", created_room.pk)
    else:
        form = RoomForm()
    return render(request, "chat/room_form.html", {
        "form": form,
    }) 

@login_required        
def room_chat(request, room_pk):
    room = get_object_or_404(Room, pk=room_pk)
    return render(request, "chat/room_chat.html", {
        "room": room,
    })

@login_required
def room_delete(request, room_pk):
    room = get_object_or_404(Room, pk=room_pk)
    
    #권한체크, 백엔드 단에서 권한체크는 필수.
    if room.owner != request.user:
        messages.error(request, "채팅방 소유자가 아닙니다.")
        return redirect("chat:index")
    
    if request.method == "POST":
        room.delete() # HARD DELETE :  데이터베이스에서 삭제
        messages.success(request, "채팅방을 삭제했습니다.")
        return redirect("chat:index")
    
    return render(request, "chat/room_confirm_delete.html", {
        "room": room,
    })
    

@login_required
def room_users(request, room_pk):
    room = get_object_or_404(Room, pk=room_pk)
    
    #현 채팅방에 새로운 접속여부 체킹
    if not room.is_joined_user(request.user):
        return HttpResponse("Unauthorized user", status=401)
    
    username_list = room.get_online_usernames()
    
    return JsonResponse({
        "username_list": username_list,
    })

# room_new 뷰의 클래스 기반 뷰(Class Based View) 구현
# 좌측 room_new FBV(함수 기반 뷰)와 거의 동일한 동작

class RoomCreateView(LoginRequiredMixin, CreateView):
    form_class = RoomForm
    template_name = "chat/room_form.html"
    
    def get_success_url(self):
        created_room = self.object
        return resolve_url("chat:room_chat", created_room.pk)
    
room_new = RoomCreateView.as_view()