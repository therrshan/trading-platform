"""
WSGI config for Trading Platform.

This module contains the WSGI application used by Django's development server
and any production WSGI deployments. It should expose a module-level variable
named ``application``.

For production deployments, this is used with traditional web servers like
Apache, Nginx + uWSGI, or Gunicorn for HTTP-only traffic.
For WebSocket support, use ASGI instead.
"""

import os
import sys
from pathlib import Path
from django.core.wsgi import get_wsgi_application

# Add the project directory to Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# Set default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_platform.settings.development')

# Create WSGI application
application = get_wsgi_application()

# Production WSGI configuration with middleware
if os.environ.get('DJANGO_SETTINGS_MODULE') == 'trading_platform.settings.production':
    from apps.analytics.middleware import WSGIMetricsMiddleware, WSGISecurityMiddleware
    
    # Wrap with production middleware
    application = WSGIMetricsMiddleware(
        WSGISecurityMiddleware(application)
    )

# Health check endpoint for load balancers
def health_check_application(environ, start_response):
    """
    Simple health check for load balancers and monitoring systems.
    This bypasses Django for faster response times.
    """
    if environ.get('PATH_INFO') == '/health/':
        try:
            # Basic health checks
            from django.db import connection
            from django.core.cache import cache
            
            # Test database connection
            with connection.cursor() as cursor:
                cursor.execute('SELECT 1')
            
            # Test cache connection  
            cache.set('health_check', 'ok', 10)
            cache.get('health_check')
            
            # Return healthy response
            status = '200 OK'
            headers = [
                ('Content-Type', 'application/json'),
                ('Cache-Control', 'no-cache'),
            ]
            start_response(status, headers)
            return [b'{"status": "healthy", "timestamp": "' + 
                   str(int(time.time())).encode() + b'"}']
            
        except Exception as e:
            # Return unhealthy response
            status = '503 Service Unavailable'
            headers = [
                ('Content-Type', 'application/json'),
                ('Cache-Control', 'no-cache'),
            ]
            start_response(status, headers)
            return [b'{"status": "unhealthy", "error": "' + 
                   str(e).encode() + b'"}']
    
    # Pass through to Django application
    return application(environ, start_response)

# Use health check wrapper in production
if os.environ.get('DJANGO_SETTINGS_MODULE') == 'trading_platform.settings.production':
    import time
    application = health_check_application