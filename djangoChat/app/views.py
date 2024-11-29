from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render

from djangoChat.app.models import Post

def echo_page(request):
    return render(request, "app/echo_page.html")

def liveblog_index(request: HttpRequest) -> HttpResponse:
    post_list = Post.objects.all()
    return render(request, "app/liveblog_index.html", {
        "post_list": post_list,
    })
    
def post_partial(request: HttpRequest, post_id) -> HttpResponse:
    post = get_object_or_404(Post, pk=post_id)
    return render(request, "app/partial/post.html", {
        "post":post,
    })