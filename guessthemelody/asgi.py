"""
ASGI config for guessthemelody project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os

import django
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'guessthemelody.settings')
django.setup()

from game_app.routing import ws_urlpatterns

application = ProtocolTypeRouter(
	{
		'http': get_asgi_application(),
		'websocket': URLRouter(ws_urlpatterns)
	}
)
