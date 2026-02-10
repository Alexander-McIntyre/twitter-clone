import datetime, json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from .models import Messages, Account, Chat

class ChatConsumer(WebsocketConsumer):
	def connect(self):
		self.chat_pk = self.scope['url_route']['kwargs']['pk']
		self.chat_name = 'chat_%s' % self.chat_pk
		async_to_sync(self.channel_layer.group_add)(
				self.chat_name,
				self.channel_name
				)
		self.accept()

	
	def disconnect(self, close_code):
		async_to_sync(self.channel_layer.group_discard)(
				self.chat_name,
				self.channel_name
				)


	def receive(self, text_data):
		text_data_json = json.loads(text_data)
		message = text_data_json['message']
		account_id = text_data_json['account_id']
		account = Account.objects.get(pk=account_id)
		chat = Chat.objects.get(pk=self.chat_pk)
		message_db = Messages(
				room = chat,
				author=account,
				context=message,
				date=datetime.datetime.now()
				)
		message_db.save()
		async_to_sync(self.channel_layer.group_send)(
				self.chat_name,
				{
					'type': 'chat_message',
					'message': account.display_name + ': ' + message,
					'avatar': account.avatar_img.url,
				})



	def chat_message(self,event):
		message = event['message']
		avatar = event['avatar']
		self.send(text_data=json.dumps({
			'message': event['message'],
			'avatar': str(event['avatar']),
		}))

