"""
Production settings for Trading Platform.
This file contains production-specific configurations with security and performance optimizations.
"""

from .base import *
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.redis import RedisIntegration

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Allowed hosts - must be set properly in production
ALLOWED_HOSTS = env('ALLOWED_HOSTS')
if not ALLOWED_HOSTS:
    raise ValueError("ALLOWED_HOSTS must be set in production environment")

# Database configuration for production
DATABASES['default'].update({
    'OPTIONS': {
        'options': '-c default_transaction_isolation=repeatable_read',
        'sslmode': 'require',  # Require SSL connections
        'connect_timeout': 10,
        'application_name': 'trading_platform_prod',
    },
    'CONN_MAX_AGE': 600,  # Connection pooling
    'CONN_HEALTH_CHECKS': True,
})

# Production database connection pooling
DATABASES['default']['OPTIONS'].update({
    'MAX_CONNS': 20,
    'MIN_CONNS': 5,
})

# Enhanced security settings for production
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# Session and CSRF security
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'
CSRF_TRUSTED_ORIGINS = env('CSRF_TRUSTED_ORIGINS', default=[])

# Content Security Policy
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'", "cdn.jsdelivr.net", "cdnjs.cloudflare.com")
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'", "fonts.googleapis.com")
CSP_FONT_SRC = ("'self'", "fonts.gstatic.com")
CSP_IMG_SRC = ("'self'", "data:", "*.tradingview.com")
CSP_CONNECT_SRC = ("'self'", "wss:", "*.alphavantage.co", "*.polygon.io")

# Email configuration for production
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST')
EMAIL_PORT = env('EMAIL_PORT', default=587)
EMAIL_USE_TLS = env('EMAIL_USE_TLS', default=True)
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')

# Static files with WhiteNoise for production
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = False

# Media files - use AWS S3 in production
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = env('AWS_S3_REGION_NAME', default='us-east-1')
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
AWS_DEFAULT_ACL = 'private'
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}
AWS_S3_FILE_OVERWRITE = False

# Cache configuration for production - Redis with compression
CACHES['default'].update({
    'OPTIONS': {
        'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        'SERIALIZER': 'django_redis.serializers.json.JSONSerializer',
        'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
        'CONNECTION_POOL_KWARGS': {
            'max_connections': 50,
            'retry_on_timeout': True,
        },
    },
    'TIMEOUT': 3600,  # 1 hour default timeout
})

# Session configuration for production
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
SESSION_CACHE_ALIAS = 'default'
SESSION_COOKIE_AGE = 43200  # 12 hours

# Celery configuration for production
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_TASK_ACKS_LATE = True
CELERY_WORKER_PREFETCH_MULTIPLIER = 4
CELERY_TASK_COMPRESSION = 'gzip'
CELERY_RESULT_COMPRESSION = 'gzip'
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

# Celery monitoring and error handling
CELERY_SEND_TASK_ERROR_EMAILS = True
CELERY_TASK_REJECT_ON_WORKER_LOST = True
CELERY_WORKER_DISABLE_RATE_LIMITS = False

# Django Channels for production
CHANNEL_LAYERS['default']['CONFIG'].update({
    'capacity': 2000,
    'expiry': 30,
    'group_expiry': 86400,
    'symmetric_encryption_keys': [env('CHANNELS_ENCRYPTION_KEY', default=SECRET_KEY)],
})

# Logging configuration for production
LOGGING['handlers'].update({
    'file': {
        'level': 'INFO',
        'class': 'logging.handlers.RotatingFileHandler',
        'filename': '/var/log/trading_platform/app.log',
        'maxBytes': 1024*1024*100,  # 100 MB
        'backupCount': 10,
        'formatter': 'json',
    },
    'error_file': {
        'level': 'ERROR',
        'class': 'logging.handlers.RotatingFileHandler',
        'filename': '/var/log/trading_platform/error.log',
        'maxBytes': 1024*1024*50,  # 50 MB
        'backupCount': 5,
        'formatter': 'json',
    },
    'security_file': {
        'level': 'WARNING',
        'class': 'logging.handlers.RotatingFileHandler',
        'filename': '/var/log/trading_platform/security.log',
        'maxBytes': 1024*1024*20,  # 20 MB
        'backupCount': 10,
        'formatter': 'json',
    },
})

# Update loggers for production
LOGGING['loggers'].update({
    'django': {
        'handlers': ['file', 'error_file'],
        'level': 'INFO',
        'propagate': False,
    },
    'django.security': {
        'handlers': ['security_file'],
        'level': 'WARNING',
        'propagate': False,
    },
    'apps.market_data': {
        'handlers': ['file'],
        'level': 'INFO',
        'propagate': False,
    },
    'apps.ml_models': {
        'handlers': ['file'],
        'level': 'INFO',
        'propagate': False,
    },
})

# Sentry configuration for error tracking
SENTRY_DSN = env('SENTRY_DSN', default=None)
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(auto_enabling=True),
            CeleryIntegration(),
            RedisIntegration(),
        ],
        traces_sample_rate=0.1,
        send_default_pii=False,
        environment="production",
        release=env('APP_VERSION', default='1.0.0'),
    )

# Market data configuration for production
MARKET_DATA_PROVIDERS.update({
    'DEVELOPMENT_MODE': False,
    'USE_MOCK_DATA': False,
    'ENABLE_REAL_TIME_STREAMING': True,
    'FAILOVER_ENABLED': True,
    'PRIMARY_PROVIDER': 'ALPHA_VANTAGE',
    'BACKUP_PROVIDERS': ['POLYGON', 'FINNHUB'],
})

# ML settings for production
ML_SETTINGS.update({
    'MODEL_UPDATE_INTERVAL': 3600,  # 1 hour
    'BATCH_SIZE': 64,  # Larger batch size for production
    'EPOCHS': 100,
    'USE_GPU': env('USE_GPU', default=True),
    'MODEL_VERSIONING': True,
    'ENABLE_A_B_TESTING': True,
    'MODEL_MONITORING': True,
})

# Risk management for production
RISK_MANAGEMENT.update({
    'ENABLE_REAL_TIME_MONITORING': True,
    'ALERT_THRESHOLD_BREACH': True,
    'AUTO_HEDGE_ENABLED': env('AUTO_HEDGE_ENABLED', default=False),
    'COMPLIANCE_REPORTING': True,
    'AUDIT_TRAIL_ENABLED': True,
})

# Trading platform settings for production
TRADING_PLATFORM_SETTINGS.update({
    'ENABLE_LIVE_TRADING': env('ENABLE_LIVE_TRADING', default=False),
    'REQUIRE_TWO_FACTOR_AUTH': True,
    'ENABLE_REAL_TIME_DATA': True,
    'DATA_RETENTION_DAYS': 2555,  # 7 years for compliance
    'ENABLE_AUDIT_LOGGING': True,
    'RATE_LIMITING_ENABLED': True,
})

# Django REST Framework for production
REST_FRAMEWORK.update({
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
        'trading': '10000/hour',  # Higher limits for trading operations
    },
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.URLPathVersioning',
})

# Performance monitoring for production
ENABLE_QUERY_PROFILING = False  # Disable in production for performance
SLOW_QUERY_THRESHOLD = 1.0  # 1 second threshold

# Additional security middleware for production
MIDDLEWARE.insert(1, 'django.middleware.security.SecurityMiddleware')
MIDDLEWARE.append('apps.security.middleware.SecurityAuditMiddleware')

# Production-specific settings
PRODUCTION_SETTINGS = {
    'HEALTH_CHECK_ENABLED': True,
    'METRICS_COLLECTION': True,
    'AUTOMATED_BACKUPS': True,
    'DISASTER_RECOVERY': True,
    'LOAD_BALANCING': True,
    'AUTO_SCALING': env('AUTO_SCALING', default=False),
    'MAINTENANCE_MODE': env('MAINTENANCE_MODE', default=False),
}

# WebRTC production configuration
WEBRTC_SETTINGS.update({
    'ICE_SERVERS': [
        {'urls': 'stun:stun.l.google.com:19302'},
        {
            'urls': env('WEBRTC_TURN_SERVER'),
            'username': env('WEBRTC_TURN_USERNAME'),
            'credential': env('WEBRTC_TURN_PASSWORD'),
        },
    ],
    'ENABLE_RECORDING': env('WEBRTC_ENABLE_RECORDING', default=False),
    'MAX_CONNECTIONS': 1000,
})

# Compliance and regulatory settings
COMPLIANCE_SETTINGS = {
    'GDPR_COMPLIANCE': True,
    'SOX_COMPLIANCE': True,
    'MiFID_II_COMPLIANCE': True,
    'DATA_ANONYMIZATION': True,
    'RIGHT_TO_BE_FORGOTTEN': True,
    'AUDIT_LOG_RETENTION': 2555,  # 7 years
}

# Ensure critical environment variables are set
REQUIRED_ENV_VARS = [
    'SECRET_KEY',
    'ALLOWED_HOSTS',
    'DB_PASSWORD',
    'EMAIL_HOST_PASSWORD',
    'AWS_ACCESS_KEY_ID',
    'AWS_SECRET_ACCESS_KEY',
]

for var in REQUIRED_ENV_VARS:
    if not env(var, default=None):
        raise ValueError(f"Required environment variable {var} is not set")

print("Production settings loaded successfully!")
print("Security features enabled")
print("Performance optimizations active")
print("Compliance features enabled")