import json
from channels.generic.websocket import WebsocketConsumer

class UserStatusConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        self.send_status_update('offline')

    def send_status_update(self, status):
        self.send(text_data=json.dumps({
            'status': status
        }))
