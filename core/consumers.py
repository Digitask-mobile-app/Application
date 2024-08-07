import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer


# class StatusConsumer(AsyncWebsocketConsumer):
#     online_users = {}

#     async def connect(self):
#         await self.accept()
#         self.user_id = self.scope['user'].id if self.scope['user'].is_authenticated else None
       
#         if self.user_id:
#             channel_layer = get_channel_layer()
#             await channel_layer.group_add(
#                 'status_updates',
#                 self.channel_name
#             )
#             StatusConsumer.online_users[self.user_id] = self.channel_name
#             await self.update_user_status(self.user_id, True)
#             await self.broadcast_status(self.user_id, 'online')
#             print(f"User {self.user_id} connected and status set to online.")
#         else:
#             print("Unauthenticated user tried to connect.")

#     async def disconnect(self, close_code):
#         if self.user_id in StatusConsumer.online_users:
#             del StatusConsumer.online_users[self.user_id]
#             await self.update_user_status(self.user_id, False)
#             await self.broadcast_status(self.user_id, 'offline')
#             print(f"User {self.user_id} disconnected and status set to offline.")

#     @database_sync_to_async
#     def update_user_status(self, user_id, online):
#         from accounts.models import User
#         try:
#             user = User.objects.get(id=user_id)
#             user.is_online = online
#             user.save()
#         except User.DoesNotExist:
#             print(f"User with ID {user_id} does not exist.")
#         except Exception as e:
#             print(f"Error updating user status: {e}")


#     async def receive(self, text_data):
#         print(f"Received WebSocket message: {text_data}")
#         data = json.loads(text_data)
#         user_id = data.get('userId')
#         status = data.get('status')

#         if user_id and status:
#             await self.broadcast_status(user_id, status)
#         else:
#             print(f"Invalid message received: {text_data}")

#     async def broadcast_status(self, user_id, status):
#         channel_layer = get_channel_layer()
#         await channel_layer.group_send(
#             'status_updates',
#             {
#                 'type': 'user_status',
#                 'user_id': user_id,
#                 'status': status
#             }
#         )
#         print(f"Broadcasting status: {status} user: {user_id}")

#     async def user_status(self, event):
#         await self.send(text_data=json.dumps({
#             'userId': event['user_id'],
#             'status': event['status']
#         }))
#         print(f"Status: {event['status']} user: {event['user_id']}")


class StatusConsumer(AsyncWebsocketConsumer):
    online_users = {}
    async def connect(self):
        from urllib.parse import parse_qs
        await self.accept()
        query_string = self.scope.get("query_string", b"").decode()
        query_params = parse_qs(query_string)
        email = query_params.get("email", [None])[0]

        user = self.scope['user']
     
        channel_layer = get_channel_layer()
        await channel_layer.group_add(
            "status",
            self.channel_name
        )
        StatusConsumer.online_users[user.id] = self.channel_name
        await channel_layer.group_send(
                "status",
                {
                    "type": "chat.message",
                    "text": 'text_data',
                },
            )
        await self.broadcast_message({user.id:'online'})

    async def disconnect(self, close_code):
        channel_layer = get_channel_layer()
        await channel_layer.group_discard(
            "status",
            self.channel_name
        )
        print("WebSocket connection closed.")

    async def receive(self, text_data):
        print(f"Received WebSocket message: {text_data}")
        user = self.scope['user']
        print(user,'user------------------------')
        data = json.loads(text_data)
        message = data.get('message', 'Bu ne ucun var bilmirem')
        data = json.loads(text_data)
        
        await self.broadcast_message(message)
     

    async def broadcast_message(self, message):
        user = self.scope['user']
        await self.send(text_data=json.dumps({
            'message': message
        }))
    