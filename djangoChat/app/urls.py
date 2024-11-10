from django.urls import path
from app import views

urlpatterns = [
    path("", views.echo_page, name='echo_page')
]
