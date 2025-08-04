"""
Development settings for Trading Platform.
This file contains development-specific configurations.
"""

from .base import *
import socket

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Allowed hosts for development
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0', '[::1]']

# Add django-debug-toolbar for development
if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware'] + MIDDLEWARE

# Database configuration for development
DATABASES['default'].update({
    'OPTIONS': {
        'options': '-c default_transaction_isolation=read_committed'
    },
    'CONN_MAX_AGE': 0,  # Disable connection pooling in development
})

# Enable query logging in development
LOGGING['loggers']['django.db.backends'] = {
    'level': 'DEBUG',
    'handlers': ['console'],
    'propagate': False,
}

# Debug toolbar configuration
if DEBUG:
    # Get local IP for Docker support
    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS = ['127.0.0.1', '10.0.2.2'] + [ip[: ip.rfind(".")] + ".1" for ip in ips]
    
    DEBUG_TOOLBAR_CONFIG = {
        'DISABLE_PANELS': [
            'debug_toolbar.panels.redirects.RedirectsPanel',
        ],
        'SHOW_TEMPLATE_CONTEXT': True,
        'SHOW_TOOLBAR_CALLBACK': lambda request: DEBUG,
    }

# Email backend for development - print to console
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Cache configuration - use dummy cache for development
CACHES['default'] = {
    'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
}

# Static files configuration for development
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Media files served by Django in development
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# CORS settings for development - allow all origins
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# WebRTC settings for local development
WEBRTC_SETTINGS.update({
    'ICE_SERVERS': [
        {'urls': 'stun:stun.l.google.com:19302'},
        {'urls': 'stun:stun1.l.google.com:19302'},
    ],
})

# Celery configuration for development
CELERY_TASK_ALWAYS_EAGER = False  # Set to True to run tasks synchronously
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

# Django Channels for development
CHANNEL_LAYERS['default']['CONFIG'].update({
    'capacity': 100,  # Lower capacity for development
    'expiry': 60,
})

# Market data settings for development
MARKET_DATA_PROVIDERS.update({
    'DEVELOPMENT_MODE': True,
    'USE_MOCK_DATA': env('USE_MOCK_DATA', default=True),
    'MOCK_DATA_PATH': BASE_DIR / 'tests' / 'fixtures' / 'market_data.json',
})

# ML settings for development
ML_SETTINGS.update({
    'MODEL_UPDATE_INTERVAL': 300,  # 5 minutes for faster testing
    'BATCH_SIZE': 16,  # Smaller batch size for development
    'EPOCHS': 10,  # Fewer epochs for faster training
    'USE_GPU': False,  # Disable GPU for development compatibility
    'ENABLE_MODEL_CACHING': True,
})

# Risk management - more lenient for development
RISK_MANAGEMENT.update({
    'MAX_POSITION_SIZE': 10000,  # Lower limits for testing
    'MAX_DAILY_LOSS': 500,
    'ENABLE_PAPER_TRADING_ONLY': True,  # Safety measure
})

# Trading platform settings for development
TRADING_PLATFORM_SETTINGS.update({
    'ENABLE_PAPER_TRADING': True,
    'ENABLE_LIVE_TRADING': False,  # Never enable in development
    'ENABLE_MOCK_TRADING': True,
    'MOCK_INITIAL_BALANCE': 100000,  # $100k play money
    'ENABLE_REAL_TIME_DATA': False,  # Use cached/mock data
})

# Logging configuration for development
LOGGING['handlers']['console']['level'] = 'DEBUG'
LOGGING['loggers']['apps.market_data']['level'] = 'DEBUG'
LOGGING['loggers']['apps.ml_models']['level'] = 'DEBUG'

# Add development-specific loggers
LOGGING['loggers'].update({
    'trading_platform': {
        'handlers': ['console'],
        'level': 'DEBUG',
        'propagate': False,
    },
    'celery.task': {
        'handlers': ['console'],
        'level': 'DEBUG',
        'propagate': False,
    },
})

# Django REST Framework for development
REST_FRAMEWORK.update({
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',  # Enable browsable API
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '1000/hour',  # More generous limits for development
        'user': '10000/hour'
    },
})

# Security settings - relaxed for development
SECURE_SSL_REDIRECT = False
SECURE_BROWSER_XSS_FILTER = False
SECURE_CONTENT_TYPE_NOSNIFF = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_HSTS_SECONDS = 0

# Performance monitoring - enabled in development
ENABLE_QUERY_PROFILING = True
SLOW_QUERY_THRESHOLD = 0.1  # Lower threshold to catch slow queries

# File upload limits - higher for development testing
FILE_UPLOAD_MAX_MEMORY_SIZE = 50242880  # 50MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 50242880  # 50MB

# Development-specific middleware
MIDDLEWARE.insert(0, 'corsheaders.middleware.CorsMiddleware')

# Additional development apps
INSTALLED_APPS += [
    'django_extensions',  # shell_plus and other utilities
]

# Shell plus configuration
SHELL_PLUS_PRE_IMPORTS = [
    ('apps.market_data.models', '*'),
    ('apps.portfolio.models', '*'),
    ('apps.ml_models.models', '*'),
    ('pandas', 'pd'),
    ('numpy', 'np'),
]

# Custom development settings
DEVELOPMENT_SETTINGS = {
    'ENABLE_API_DOCS': True,
    'ENABLE_ADMIN_INTERFACE': True,
    'AUTO_RELOAD_MODELS': True,
    'LOG_SQL_QUERIES': True,
    'MOCK_EXTERNAL_APIS': True,
    'SIMULATE_MARKET_CONDITIONS': True,
    'ENABLE_TEST_DATA_GENERATION': True,
}

print("🚀 Development settings loaded successfully!")
print(f"🔧 Debug mode: {DEBUG}")
print(f"📊 Mock data enabled: {MARKET_DATA_PROVIDERS.get('USE_MOCK_DATA', False)}")
print(f"🎯 Paper trading only: {RISK_MANAGEMENT.get('ENABLE_PAPER_TRADING_ONLY', True)}")