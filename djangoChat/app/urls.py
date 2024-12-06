from django.urls import path, include
from app import views

urlpatterns = [
    path("", views.echo_page, name='echo_page'),
    path("liveblog/",views.liveblog_index),
    path("liveblog/posts/<int:post_id>/", views.post_partial, name="post_partial"),
    path('chat/', include('chat.urls')),
]
