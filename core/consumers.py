import json
from channels.generic.websocket import WebsocketConsumer
from channels.layers import get_channel_layer
from accounts.models import User
import logging
logger = logging.getLogger(__name__)

class StatusConsumer(WebsocketConsumer):
    online_users = {}
    
    def connect(self):
        self.accept()
        self.user_id = self.scope['user'].id if self.scope['user'].is_authenticated else None
        if self.user_id:
            StatusConsumer.online_users[self.user_id] = self.channel_name
            self.update_user_status(self.user_id, True)
            self.broadcast_status(self.user_id, 'online')
            logger.info(f'User {self.user_id} connected and status set to online.')

    def disconnect(self, close_code):
        if self.user_id in StatusConsumer.online_users:
            del StatusConsumer.online_users[self.user_id]
            self.update_user_status(self.user_id, False)
            self.broadcast_status(self.user_id, 'offline')
            logger.info(f'User {self.user_id} disconnected and status set to offline.')


    def update_user_status(self, user_id, online):
        try:
            user = User.objects.get(id=user_id)
            user.is_online = online
            user.save()
        except User.DoesNotExist:
            pass

    def receive(self, text_data):
        data = json.loads(text_data)
        user_id = data.get('userId')
        status = data.get('status')

        if user_id and status:
            self.broadcast_status(user_id, status)

    def broadcast_status(self, user_id, status):
        channel_layer = get_channel_layer()
        channel_layer.group_send(
            'status_updates',
            {
                'type': 'user_status',
                'user_id': user_id,
                'status': status
            }
        )

    def user_status(self, event):
        self.send(text_data=json.dumps({
            'userId': event['user_id'],
            'status': event['status']
        }))
