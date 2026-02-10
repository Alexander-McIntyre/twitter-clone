from . import consumers
from django.urls import path
websocket_urlpatterns = [
	path('ws/core/chat/<int:pk>/', consumers.ChatConsumer.as_asgi()),
]
