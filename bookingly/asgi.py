"""
ASGI config for bookingly project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter,URLRouter
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookingly.settings')
from seller.routing import url_patterns
application = ProtocolTypeRouter(
    {
        "http":get_asgi_application(),
        "websocket":URLRouter(
            url_patterns
        )
    }
)
