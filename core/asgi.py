import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import core.routing  
from channels.security.websocket import AllowedHostsOriginValidator

import django
django.setup()
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                core.routing.websocket_urlpatterns
            )
        )
    ),
})