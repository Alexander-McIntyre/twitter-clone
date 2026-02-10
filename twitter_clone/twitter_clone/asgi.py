import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'twitter_clone.settings')
import django
django.setup()

from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from core.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
	"http": get_asgi_application(),
	"websocket": AuthMiddlewareStack(
		URLRouter(websocket_urlpatterns)
		)
	})
