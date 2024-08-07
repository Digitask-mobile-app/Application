import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from channels.sessions import SessionMiddlewareStack
from .routing import websocket_urlpatterns

from urllib.parse import parse_qs
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

django_asgi_app = get_asgi_application()

@database_sync_to_async
def get_user_from_token(token_string):
    from rest_framework.authtoken.models import Token
    try:
        token = Token.objects.get(key=token_string)
        return token.user
    except Token.DoesNotExist:
        return AnonymousUser()

class TokenAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        query_string = scope.get("query_string", b"").decode()
        query_params = parse_qs(query_string)
        token = query_params.get("token", [None])[0]
        scope["user"] = await get_user_from_token(token)
        return await self.inner(scope, receive, send)

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(
        TokenAuthMiddleware(
            AuthMiddlewareStack(
                URLRouter(
                    websocket_urlpatterns
                )
            )
        )
    ),
})
