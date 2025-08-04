"""
Main URL configuration for Trading Platform.
This file defines the root URL routing for the application.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

# API Router for ViewSets
api_router = DefaultRouter()

# Health check and status endpoints
from apps.analytics.views import HealthCheckView, SystemStatusView

urlpatterns = [
    # Admin interface
    path('admin/', admin.site.urls),
    
    # Health and monitoring endpoints
    path('health/', HealthCheckView.as_view(), name='health_check'),
    path('status/', SystemStatusView.as_view(), name='system_status'),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # API v1 endpoints
    path('api/v1/auth/', include('apps.authentication.urls')),
    path('api/v1/market-data/', include('apps.market_data.urls')),
    path('api/v1/portfolio/', include('apps.portfolio.urls')),
    path('api/v1/analytics/', include('apps.analytics.urls')),
    path('api/v1/ml-models/', include('apps.ml_models.urls')),
    
    # ViewSet routes from router
    path('api/v1/', include(api_router.urls)),
    
    # WebRTC signaling endpoints
    path('api/v1/webrtc/', include('apps.market_data.webrtc_urls')),
    
    # Main application views
    path('dashboard/', TemplateView.as_view(template_name='dashboard/index.html'), name='dashboard'),
    path('trading/', TemplateView.as_view(template_name='trading/interface.html'), name='trading'),
    path('analytics/', TemplateView.as_view(template_name='analytics/dashboard.html'), name='analytics_dashboard'),
    
    # Root redirect to dashboard
    path('', TemplateView.as_view(template_name='dashboard/index.html'), name='home'),
]

# Development-specific URLs
if settings.DEBUG:
    # Debug toolbar
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
    
    # Serve media files in development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Development endpoints for testing
    urlpatterns += [
        path('dev/mock-data/', include('apps.market_data.dev_urls')),
        path('dev/test-trading/', include('apps.portfolio.dev_urls')),
    ]

# Admin site customization
admin.site.site_header = 'Trading Platform Administration'
admin.site.site_title = 'Trading Platform Admin'
admin.site.index_title = 'Trading Platform Management'

# Custom error handlers
handler400 = 'apps.analytics.views.bad_request'
handler403 = 'apps.analytics.views.permission_denied'
handler404 = 'apps.analytics.views.page_not_found'
handler500 = 'apps.analytics.views.server_error'