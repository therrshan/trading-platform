"""
WebSocket routing configuration for Trading Platform.

This module defines WebSocket URL patterns for real-time features including:
- Market data streaming
- Portfolio updates
- Trading notifications
- ML model predictions
- WebRTC signaling
"""

from django.urls import re_path, path
from channels.routing import URLRouter

# Import WebSocket consumers
from apps.market_data.consumers import (
    MarketDataConsumer,
    TradingConsumer,
    WebRTCSignalingConsumer,
)
from apps.portfolio.consumers import (
    PortfolioConsumer,
    OrdersConsumer,
)
from apps.ml_models.consumers import (
    PredictionConsumer,
    ModelTrainingConsumer,
)
from apps.analytics.consumers import (
    AnalyticsConsumer,
    AlertsConsumer,
)

# WebSocket URL patterns
websocket_urlpatterns = [
    # Market Data WebSocket endpoints
    re_path(r'ws/market-data/(?P<symbol>[^/]+)/$', MarketDataConsumer.as_asgi()),
    re_path(r'ws/market-data/stream/(?P<symbols>[^/]+)/$', MarketDataConsumer.as_asgi()),
    
    # Trading WebSocket endpoints
    re_path(r'ws/trading/(?P<user_id>\w+)/$', TradingConsumer.as_asgi()),
    re_path(r'ws/orders/(?P<user_id>\w+)/$', OrdersConsumer.as_asgi()),
    
    # Portfolio WebSocket endpoints
    re_path(r'ws/portfolio/(?P<portfolio_id>\w+)/$', PortfolioConsumer.as_asgi()),
    re_path(r'ws/portfolio/(?P<portfolio_id>\w+)/positions/$', PortfolioConsumer.as_asgi()),
    
    # ML Models WebSocket endpoints
    re_path(r'ws/predictions/(?P<symbol>[^/]+)/$', PredictionConsumer.as_asgi()),
    re_path(r'ws/model-training/(?P<model_id>\w+)/$', ModelTrainingConsumer.as_asgi()),
    
    # Analytics WebSocket endpoints
    re_path(r'ws/analytics/(?P<dashboard_id>\w+)/$', AnalyticsConsumer.as_asgi()),
    re_path(r'ws/alerts/(?P<user_id>\w+)/$', AlertsConsumer.as_asgi()),
    
    # WebRTC Signaling WebSocket endpoints
    re_path(r'ws/webrtc/signaling/(?P<room_name>[^/]+)/$', WebRTCSignalingConsumer.as_asgi()),
    re_path(r'ws/webrtc/data-channel/(?P<session_id>[^/]+)/$', WebRTCSignalingConsumer.as_asgi()),
    
    # Administrative WebSocket endpoints
    re_path(r'ws/admin/system-status/$', AnalyticsConsumer.as_asgi()),
    re_path(r'ws/admin/user-activity/(?P<user_id>\w+)/$', AnalyticsConsumer.as_asgi()),
]

# Group WebSocket patterns by application for better organization
market_data_patterns = [
    re_path(r'ws/market-data/(?P<symbol>[^/]+)/$', MarketDataConsumer.as_asgi()),
    re_path(r'ws/market-data/stream/(?P<symbols>[^/]+)/$', MarketDataConsumer.as_asgi()),
    re_path(r'ws/market-data/technical-indicators/(?P<symbol>[^/]+)/$', MarketDataConsumer.as_asgi()),
]

trading_patterns = [
    re_path(r'ws/trading/(?P<user_id>\w+)/$', TradingConsumer.as_asgi()),
    re_path(r'ws/orders/(?P<user_id>\w+)/$', OrdersConsumer.as_asgi()),
    re_path(r'ws/execution/(?P<order_id>\w+)/$', TradingConsumer.as_asgi()),
]

portfolio_patterns = [
    re_path(r'ws/portfolio/(?P<portfolio_id>\w+)/$', PortfolioConsumer.as_asgi()),
    re_path(r'ws/portfolio/(?P<portfolio_id>\w+)/positions/$', PortfolioConsumer.as_asgi()),
    re_path(r'ws/portfolio/(?P<portfolio_id>\w+)/performance/$', PortfolioConsumer.as_asgi()),
]

ml_patterns = [
    re_path(r'ws/predictions/(?P<symbol>[^/]+)/$', PredictionConsumer.as_asgi()),
    re_path(r'ws/model-training/(?P<model_id>\w+)/$', ModelTrainingConsumer.as_asgi()),
    re_path(r'ws/backtesting/(?P<strategy_id>\w+)/$', PredictionConsumer.as_asgi()),
]

analytics_patterns = [
    re_path(r'ws/analytics/(?P<dashboard_id>\w+)/$', AnalyticsConsumer.as_asgi()),
    re_path(r'ws/alerts/(?P<user_id>\w+)/$', AlertsConsumer.as_asgi()),
    re_path(r'ws/risk-monitoring/(?P<portfolio_id>\w+)/$', AnalyticsConsumer.as_asgi()),
]

webrtc_patterns = [
    re_path(r'ws/webrtc/signaling/(?P<room_name>[^/]+)/$', WebRTCSignalingConsumer.as_asgi()),
    re_path(r'ws/webrtc/data-channel/(?P<session_id>[^/]+)/$', WebRTCSignalingConsumer.as_asgi()),
    re_path(r'ws/webrtc/trading-room/(?P<room_id>[^/]+)/$', WebRTCSignalingConsumer.as_asgi()),
]

# Alternative routing configuration for different environments
def get_websocket_patterns(environment='development'):
    """
    Get WebSocket patterns based on environment.
    Production might have different routing for load balancing.
    """
    base_patterns = websocket_urlpatterns
    
    if environment == 'production':
        # Add production-specific patterns
        production_patterns = [
            re_path(r'ws/health/$', AnalyticsConsumer.as_asgi()),
            re_path(r'ws/metrics/$', AnalyticsConsumer.as_asgi()),
        ]
        return base_patterns + production_patterns
    
    elif environment == 'development':
        # Add development-specific patterns
        dev_patterns = [
            re_path(r'ws/debug/(?P<debug_type>\w+)/$', AnalyticsConsumer.as_asgi()),
            re_path(r'ws/test/(?P<test_id>\w+)/$', MarketDataConsumer.as_asgi()),
        ]
        return base_patterns + dev_patterns
    
    return base_patterns

# Export patterns based on environment
import os
current_env = 'production' if 'production' in os.environ.get('DJANGO_SETTINGS_MODULE', '') else 'development'
websocket_urlpatterns = get_websocket_patterns(current_env)