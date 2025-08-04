"""
Base settings for Trading Platform.
This file contains settings common to all environments.
"""

import os
import environ
from pathlib import Path
from datetime import timedelta

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Environment variables
env = environ.Env(
    DEBUG=(bool, False),
    SECRET_KEY=(str, 'your-secret-key-change-in-production'),
    ALLOWED_HOSTS=(list, []),
)

# Read environment file
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')

ALLOWED_HOSTS = env('ALLOWED_HOSTS')

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'channels',
    'django_celery_beat',
    'django_celery_results',
    'drf_spectacular',
]

LOCAL_APPS = [
    'apps.authentication',
    'apps.market_data',
    'apps.portfolio',
    'apps.ml_models',
    'apps.analytics',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'apps.market_data.middleware.MarketDataMiddleware',  # Custom middleware
]

ROOT_URLCONF = 'trading_platform.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'trading_platform.wsgi.application'
ASGI_APPLICATION = 'trading_platform.routing.application'

# Database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME', default='trading_platform'),
        'USER': env('DB_USER', default='postgres'),
        'PASSWORD': env('DB_PASSWORD', default=''),
        'HOST': env('DB_HOST', default='localhost'),
        'PORT': env('DB_PORT', default='5432'),
        'OPTIONS': {
            'options': '-c default_transaction_isolation=repeatable_read'
        },
        'CONN_MAX_AGE': 600,
    },
    'timeseries': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('TIMESERIES_DB_NAME', default='trading_timeseries'),
        'USER': env('DB_USER', default='postgres'),
        'PASSWORD': env('DB_PASSWORD', default=''),
        'HOST': env('TIMESERIES_DB_HOST', default='localhost'),
        'PORT': env('TIMESERIES_DB_PORT', default='5433'),
        'OPTIONS': {
            'options': '-c default_transaction_isolation=read_committed'
        },
    }
}

# Database routing for time-series data
DATABASE_ROUTERS = ['apps.market_data.routers.TimeSeriesRouter']

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Redis Configuration
REDIS_URL = env('REDIS_URL', default='redis://localhost:6379/0')

# Cache Configuration
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': env('CACHE_URL', default='redis://localhost:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'SERIALIZER': 'django_redis.serializers.json.JSONSerializer',
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
        },
        'KEY_PREFIX': 'trading_platform',
        'TIMEOUT': 300,
    }
}

# Sessions
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
SESSION_COOKIE_AGE = 86400  # 24 hours

# Channels (WebSocket) Configuration
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [env('CHANNEL_LAYER_URL', default='redis://localhost:6379/2')],
            'capacity': 1500,
            'expiry': 10,
        },
    },
}

# Celery Configuration
CELERY_BROKER_URL = env('CELERY_BROKER_URL', default='redis://localhost:6379/3')
CELERY_RESULT_BACKEND = env('CELERY_RESULT_BACKEND', default='redis://localhost:6379/4')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 100,
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour'
    },
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# JWT Configuration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(seconds=env('JWT_ACCESS_TOKEN_LIFETIME', default=3600)),
    'REFRESH_TOKEN_LIFETIME': timedelta(seconds=env('JWT_REFRESH_TOKEN_LIFETIME', default=86400)),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': env('JWT_SECRET_KEY', default=SECRET_KEY),
    'VERIFYING_KEY': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

# CORS Configuration
CORS_ALLOW_ALL_ORIGINS = DEBUG
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React dev server
    "http://127.0.0.1:3000",
    "http://localhost:8080",
]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# API Documentation
SPECTACULAR_SETTINGS = {
    'TITLE': 'Trading Platform API',
    'DESCRIPTION': 'Real-time trading analytics and portfolio management platform',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SCHEMA_PATH_PREFIX': '/api/',
    'COMPONENT_SPLIT_REQUEST': True,
    'SORT_OPERATIONS': False,
}

# Market Data Configuration
MARKET_DATA_PROVIDERS = {
    'ALPHA_VANTAGE': {
        'API_KEY': env('ALPHA_VANTAGE_API_KEY', default=''),
        'BASE_URL': 'https://www.alphavantage.co/query',
        'RATE_LIMIT': 5,  # requests per minute
    },
    'POLYGON': {
        'API_KEY': env('POLYGON_API_KEY', default=''),
        'BASE_URL': 'https://api.polygon.io',
        'RATE_LIMIT': 5,
    },
    'FINNHUB': {
        'API_KEY': env('FINNHUB_API_KEY', default=''),
        'BASE_URL': 'https://finnhub.io/api/v1',
        'RATE_LIMIT': 60,
    }
}

# WebRTC Configuration
WEBRTC_SETTINGS = {
    'ICE_SERVERS': [
        {'urls': env('WEBRTC_ICE_SERVERS', default='stun:stun.l.google.com:19302')},
    ],
    'TURN_SERVER': env('WEBRTC_TURN_SERVER', default=''),
    'TURN_USERNAME': env('WEBRTC_TURN_USERNAME', default=''),
    'TURN_PASSWORD': env('WEBRTC_TURN_PASSWORD', default=''),
}

if WEBRTC_SETTINGS['TURN_SERVER']:
    WEBRTC_SETTINGS['ICE_SERVERS'].append({
        'urls': WEBRTC_SETTINGS['TURN_SERVER'],
        'username': WEBRTC_SETTINGS['TURN_USERNAME'],
        'credential': WEBRTC_SETTINGS['TURN_PASSWORD'],
    })

# ML Model Configuration
ML_SETTINGS = {
    'MODEL_UPDATE_INTERVAL': env('ML_MODEL_UPDATE_INTERVAL', default=3600),
    'PREDICTION_LOOKBACK_DAYS': env('PREDICTION_LOOKBACK_DAYS', default=30),
    'TECHNICAL_INDICATORS_PERIOD': env('TECHNICAL_INDICATORS_PERIOD', default=14),
    'MODEL_STORAGE_PATH': BASE_DIR / 'ml_pipeline' / 'models',
    'DATA_STORAGE_PATH': BASE_DIR / 'ml_pipeline' / 'data',
    'TRAINING_DATA_RETENTION_DAYS': 365,
    'BATCH_SIZE': 32,
    'EPOCHS': 50,
    'VALIDATION_SPLIT': 0.2,
}

# Risk Management Settings
RISK_MANAGEMENT = {
    'MAX_POSITION_SIZE': env('MAX_POSITION_SIZE', default=100000),  # USD
    'MAX_DAILY_LOSS': env('MAX_DAILY_LOSS', default=5000),  # USD
    'RISK_FREE_RATE': env('RISK_FREE_RATE', default=0.05),  # Annual rate
    'VAR_CONFIDENCE_LEVEL': 0.95,
    'STRESS_TEST_SCENARIOS': [
        {'name': 'market_crash', 'market_drop': -0.20},
        {'name': 'volatility_spike', 'vol_multiplier': 2.0},
        {'name': 'liquidity_crisis', 'spread_multiplier': 3.0},
    ]
}

# Email Configuration
EMAIL_BACKEND = env('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
if EMAIL_BACKEND == 'django.core.mail.backends.smtp.EmailBackend':
    EMAIL_HOST = env('EMAIL_HOST', default='smtp.gmail.com')
    EMAIL_PORT = env('EMAIL_PORT', default=587)
    EMAIL_USE_TLS = env('EMAIL_USE_TLS', default=True)
    EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
    EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')

DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='noreply@tradingplatform.com')
ADMIN_EMAIL = env('ADMIN_EMAIL', default='admin@tradingplatform.com')

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(name)s %(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'trading_platform.log',
            'maxBytes': 1024*1024*10,  # 10 MB
            'backupCount': 5,
            'formatter': 'json',
        },
        'market_data': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'market_data.log',
            'maxBytes': 1024*1024*50,  # 50 MB
            'backupCount': 10,
            'formatter': 'json',
        },
        'ml_models': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'ml_models.log',
            'maxBytes': 1024*1024*20,  # 20 MB
            'backupCount': 5,
            'formatter': 'json',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': env('LOG_LEVEL', default='INFO'),
        },
        'apps.market_data': {
            'handlers': ['console', 'market_data'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'apps.ml_models': {
            'handlers': ['console', 'ml_models'],
            'level': 'INFO',
            'propagate': False,
        },
        'celery': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Create logs directory if it doesn't exist
os.makedirs(BASE_DIR / 'logs', exist_ok=True)

# Performance Monitoring
ENABLE_QUERY_PROFILING = env('ENABLE_QUERY_PROFILING', default=DEBUG)
SLOW_QUERY_THRESHOLD = env('SLOW_QUERY_THRESHOLD', default=0.5)

if ENABLE_QUERY_PROFILING:
    LOGGING['loggers']['django.db.backends'] = {
        'level': 'DEBUG',
        'handlers': ['console'],
        'propagate': False,
    }

# Security Settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Custom User Model (if you want to extend default User)
# AUTH_USER_MODEL = 'authentication.User'

# Internationalization
USE_THOUSAND_SEPARATOR = True
NUMBER_GROUPING = 3

# Time zones for different markets
MARKET_TIMEZONES = {
    'NYSE': 'America/New_York',
    'NASDAQ': 'America/New_York',
    'LSE': 'Europe/London',
    'TSE': 'Asia/Tokyo',
    'SSE': 'Asia/Shanghai',
}

# File Upload Settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB

# Custom Settings for Trading Platform
TRADING_PLATFORM_SETTINGS = {
    'ENABLE_PAPER_TRADING': True,
    'ENABLE_LIVE_TRADING': False,  # Disable by default for safety
    'DEFAULT_CURRENCY': 'USD',
    'SUPPORTED_CURRENCIES': ['USD', 'EUR', 'GBP', 'JPY'],
    'MINIMUM_ACCOUNT_BALANCE': 1000,  # USD
    'COMMISSION_RATE': 0.001,  # 0.1%
    'MARGIN_REQUIREMENT': 0.5,  # 50%
}