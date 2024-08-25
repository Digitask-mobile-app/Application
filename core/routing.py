from django.urls import re_path
from .consumers import StatusConsumer,UserListConsumer,NotificationConsumer
from .chatConsumer import ChatConsumer

websocket_urlpatterns = [
    re_path(r'ws/status/$', StatusConsumer.as_asgi()),
    re_path(r'ws/userlist/$', UserListConsumer.as_asgi()),
    re_path(r'ws/notification/$', NotificationConsumer.as_asgi()),
    re_path(r'ws/ChatConsumer/$', ChatConsumer.as_asgi()),
]