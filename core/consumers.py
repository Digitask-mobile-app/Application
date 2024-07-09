import json
from channels.generic.websocket import WebsocketConsumer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.contrib.auth import get_user_model
from channels.generic.websocket import AsyncWebsocketConsumer
User = get_user_model()


class StatusConsumer(AsyncWebsocketConsumer):
    online_users = {}

    async def connect(self):
        await self.accept()

        self.user_id = self.scope['user'].id if self.scope['user'].is_authenticated else None
        if self.user_id:
            StatusConsumer.online_users[self.user_id] = self.channel_name
            await self.update_user_status(self.user_id, True)
            await self.broadcast_status(self.user_id, 'online')

    async def disconnect(self, close_code):
        if self.user_id in StatusConsumer.online_users:
            del StatusConsumer.online_users[self.user_id]
            await self.update_user_status(self.user_id, False)
            await self.broadcast_status(self.user_id, 'offline')

    async def update_user_status(self, user_id, online):
        try:
            user = await self.get_user(user_id)
            user.is_online = online
            await user.save()
        except User.DoesNotExist:
            pass

    async def receive(self, text_data):
        data = json.loads(text_data)
        user_id = data.get('userId')
        status = data.get('status')

        if user_id and status:
            await self.broadcast_status(user_id, status)

    async def broadcast_status(self, user_id, status):
        channel_layer = self.channel_layer
        await channel_layer.group_send(
            'status_updates',
            {
                'type': 'user_status',
                'user_id': user_id,
                'status': status
            }
        )

    async def user_status(self, event):
        await self.send(text_data=json.dumps({
            'userId': event['user_id'],
            'status': event['status']
        }))

    async def get_user(self, user_id):
        try:
            return await self.get_django_user_model().objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    def get_django_user_model(self):
        # Django'nun User modelini döndürür
        return User

    async def get_django_user(self, user_id):
        # Asenkron şekilde Django'nun User modelini getirir
        try:
            return await self.get_django_user_model().objects.get(id=user_id)
        except User.DoesNotExist:
            return None