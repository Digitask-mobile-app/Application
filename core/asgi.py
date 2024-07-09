import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import core.routing  
from channels.security.websocket import AllowedHostsOriginValidator
from .consumers import StatusConsumer
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
django_asgi_app = get_asgi_application()
from django.urls import path
application = ProtocolTypeRouter({
    "http": get_asgi_application(),
      "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter([
                path("ws/status/", StatusConsumer.as_asgi()),

            ])
        )
    ),
})