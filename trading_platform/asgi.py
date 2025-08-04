"""
ASGI config for Trading Platform.

This module contains the ASGI application used by Django's development server
and any production ASGI deployments. It configures Django to handle both HTTP
and WebSocket connections for real-time trading features.

It exposes the ASGI callable as a module-level variable named ``application``.
"""

import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

# Set default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_platform.settings.development')

# Initialize Django before importing routing
django.setup()

# Import routing after Django setup
from trading_platform.routing import websocket_urlpatterns
from apps.market_data.middleware import WebSocketJWTAuthMiddleware

# ASGI application configuration
application = ProtocolTypeRouter({
    # HTTP requests - standard Django ASGI application
    "http": get_asgi_application(),
    
    # WebSocket connections - for real-time features
    "websocket": AllowedHostsOriginValidator(
        WebSocketJWTAuthMiddleware(
            AuthMiddlewareStack(
                URLRouter(websocket_urlpatterns)
            )
        )
    ),
})

# Production ASGI configuration with additional middleware
if os.environ.get('DJANGO_SETTINGS_MODULE') == 'trading_platform.settings.production':
    from apps.analytics.middleware import ASGIMetricsMiddleware, ASGILoggingMiddleware
    
    # Wrap with production middleware
    application = ASGIMetricsMiddleware(
        ASGILoggingMiddleware(application)
    )