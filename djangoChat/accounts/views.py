from django.shortcuts import render
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

# 프로필 뷰 호출은 로그인 시에만 의미가 있다.

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/profile.html"

login = LoginView.as_view(
    template_name = "partials/form.html",
    extra_context = {
        "form_name": "로그인",
        "submit_label": "로그인",
    },
)

logout = LogoutView.as_view(
    next_page="accounts:login",
)