import json
from channels.generic.websocket import WebsocketConsumer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.contrib.auth import get_user_model
from channels.generic.websocket import AsyncWebsocketConsumer
User = get_user_model()

class StatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        data = json.loads(text_data)
        # İşleme kodları
        await self.send(text_data=json.dumps({
            'message': 'Message received!'
        }))


# class StatusConsumer(WebsocketConsumer):
#     online_users = {}

#     def connect(self):
#         self.accept()

#         self.user_id = self.scope['user'].id if self.scope['user'].is_authenticated else None
#         if self.user_id:
#             StatusConsumer.online_users[self.user_id] = self.channel_name
#             self.update_user_status(self.user_id, True)
#             self.broadcast_status(self.user_id, 'online')

#     def disconnect(self, close_code):
#         if self.user_id in StatusConsumer.online_users:
#             del StatusConsumer.online_users[self.user_id]
#             self.update_user_status(self.user_id, False)
#             self.broadcast_status(self.user_id, 'offline')

#     def update_user_status(self, user_id, online):
#         try:
#             user = User.objects.get(id=user_id)
#             user.is_online = online
#             user.save()
#         except User.DoesNotExist:
#             pass

#     def receive(self, text_data):
#         data = json.loads(text_data)
#         user_id = data.get('userId')
#         status = data.get('status')

#         if user_id and status:
#             self.broadcast_status(user_id, status)

#     def broadcast_status(self, user_id, status):
#         channel_layer = get_channel_layer()
#         async_to_sync(channel_layer.group_send)(
#             'status_updates',
#             {
#                 'type': 'user_status',
#                 'user_id': user_id,
#                 'status': status
#             }
#         )

#     def user_status(self, event):
#         self.send(text_data=json.dumps({
#             'userId': event['user_id'],
#             'status': event['status']
#         }))

    