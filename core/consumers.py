import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

class StatusConsumer(AsyncWebsocketConsumer):
    online_users = {}

    async def connect(self):
        await self.accept()
        self.user_id = self.scope['user'].id if self.scope['user'].is_authenticated else None
        print('1')
        if self.user_id:
            print('2')
            channel_layer = get_channel_layer()
            await channel_layer.group_add(
                'status_updates',  
                self.channel_name  
            )
            print('3')
            StatusConsumer.online_users[self.user_id] = self.channel_name
            await self.update_user_status(self.user_id, True)
            print('4')
            await self.broadcast_status(self.user_id, 'online')

    async def disconnect(self, close_code):
        if self.user_id in StatusConsumer.online_users:
            del StatusConsumer.online_users[self.user_id]
            await self.update_user_status(self.user_id, False)
            await self.broadcast_status(self.user_id, 'offline')

    def update_user_status(self, user_id, online):
        from accounts.models import User
        try:
            user = User.objects.get(id=user_id)
            user.is_online = online
            user.save()
        except User.DoesNotExist:
            pass

    async def receive(self, text_data):
        data = json.loads(text_data)
        user_id = data.get('userId')
        status = data.get('status')

        if user_id and status:
            await self.broadcast_status(user_id, status)

    async def broadcast_status(self, user_id, status):
        channel_layer = get_channel_layer()
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