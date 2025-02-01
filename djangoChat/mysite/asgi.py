"""
ASGI config for mysite project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

# settings.py 경로에 맞춰 DJANGO_SETTINGS_MODULE 환경변수의 디폴트 값을 지정
os.environ.setdefault('DJANGO_SETTINGS_MODULE','mysite.settings')

django_asgi_app = get_asgi_application()

# 프로젝트 로딩 후에 모델/setiings에 접근하도록 설정
import app.routing
import chat.routing

#프로토콜 타입별로 서로 다른 ASGI application을 통해 처리토록 라우팅합니다.
application = ProtocolTypeRouter({
    # 지금은 http 타입에 대한 라우팅만 명시
    "http" : django_asgi_app,
    # 서비스 규모에 따라 http와 websoket을 분리하여(웹서버와 채팅서버) 운영하기도 함
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
        URLRouter(
            chat.routing.websocket_urlpatters + 
            app.routing.websocket_urlpatterns
            )
        )
    ),
})