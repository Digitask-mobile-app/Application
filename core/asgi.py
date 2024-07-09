import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import core.routing  
from channels.security.websocket import AllowedHostsOriginValidator
from django.urls import re_path
from .consumers import StatusConsumer
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"


application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": 
        AuthMiddlewareStack(
            URLRouter((
                re_path("chat/", StatusConsumer.as_asgi()),
            )
            )
        ),
})