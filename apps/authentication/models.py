"""
Authentication models for Trading Platform.

This module defines user authentication and profile models with trading-specific
features including risk profiles, account verification, and audit trails.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal
import uuid


class User(AbstractUser):
    """
    Extended User model with trading platform specific fields.
    """
    
    # Unique identifier for external systems
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    
    # Personal Information
    middle_name = models.CharField(max_length=30, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    
    # Account Status
    is_verified = models.BooleanField(default=False)
    verification_level = models.CharField(
        max_length=20,
        choices=[
            ('basic', 'Basic'),
            ('intermediate', 'Intermediate'),
            ('advanced', 'Advanced'),
            ('professional', 'Professional'),
        ],
        default='basic'
    )
    
    # Trading Related
    trading_enabled = models.BooleanField(default=False)
    paper_trading_only = models.BooleanField(default=True)
    risk_tolerance = models.CharField(
        max_length=20,
        choices=[
            ('conservative', 'Conservative'),
            ('moderate', 'Moderate'),
            ('aggressive', 'Aggressive'),
            ('expert', 'Expert'),
        ],
        default='moderate'
    )
    
    # Account Limits
    daily_trading_limit = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=Decimal('10000.00'),
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    max_position_size = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=Decimal('50000.00'),
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    
    # Security
    two_factor_enabled = models.BooleanField(default=False)
    two_factor_secret = models.CharField(max_length=32, blank=True)
    failed_login_attempts = models.PositiveIntegerField(default=0)
    account_locked_until = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    email_verified_at = models.DateTimeField(null=True, blank=True)
    last_password_change = models.DateTimeField(auto_now_add=True)
    terms_accepted_at = models.DateTimeField(null=True, blank=True)
    
    # Preferences
    timezone = models.CharField(max_length=50, default='UTC')
    preferred_currency = models.CharField(max_length=3, default='USD')
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'auth_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        indexes = [
            models.Index(fields=['uuid']),
            models.Index(fields=['is_verified', 'trading_enabled']),
            models.Index(fields=['verification_level']),
        ]
    
    def __str__(self):
        return f"{self.username} ({self.get_full_name()})"
    
    @property
    def full_name(self):
        """Return full name including middle name."""
        names = [self.first_name, self.middle_name, self.last_name]
        return ' '.join(filter(None, names))
    
    @property
    def is_account_locked(self):
        """Check if account is currently locked."""
        if self.account_locked_until:
            return timezone.now() < self.account_locked_until
        return False
    
    def can_trade(self):
        """Check if user can perform trading operations."""
        return (
            self.is_active and 
            self.is_verified and 
            self.trading_enabled and 
            not self.is_account_locked
        )
    
    def reset_failed_attempts(self):
        """Reset failed login attempts and unlock account."""
        self.failed_login_attempts = 0
        self.account_locked_until = None
        self.save(update_fields=['failed_login_attempts', 'account_locked_until'])


class UserProfile(models.Model):
    """
    Extended user profile with detailed trading information.
    """
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Professional Information
    occupation = models.CharField(max_length=100, blank=True)
    employer = models.CharField(max_length=100, blank=True)
    annual_income = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    net_worth = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    
    # Trading Experience
    trading_experience = models.CharField(
        max_length=20,
        choices=[
            ('none', 'No Experience'),
            ('beginner', 'Less than 1 year'),
            ('intermediate', '1-3 years'),
            ('experienced', '3-10 years'),
            ('expert', 'More than 10 years'),
        ],
        default='none'
    )
    
    investment_objectives = models.JSONField(
        default=list,
        help_text="List of investment objectives"
    )
    
    # Risk Assessment
    risk_score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        null=True,
        blank=True,
        help_text="Risk score from 1 (conservative) to 100 (aggressive)"
    )
    
    # Compliance and Regulatory
    is_accredited_investor = models.BooleanField(default=False)
    is_professional_investor = models.BooleanField(default=False)
    regulatory_status = models.JSONField(
        default=dict,
        help_text="Regulatory status for different jurisdictions"
    )
    
    # Address Information
    address_line1 = models.CharField(max_length=255, blank=True)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state_province = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)
    
    # Account Settings
    default_order_size = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('1000.00')
    )
    auto_rebalance = models.BooleanField(default=False)
    rebalance_threshold = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=Decimal('5.00'),
        help_text="Percentage threshold for auto-rebalancing"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_profiles'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        return f"Profile for {self.user.username}"
    
    @property
    def full_address(self):
        """Return formatted full address."""
        address_parts = [
            self.address_line1,
            self.address_line2,
            self.city,
            self.state_province,
            self.postal_code,
            self.country
        ]
        return ', '.join(filter(None, address_parts))


class UserSession(models.Model):
    """
    Track user sessions for security and analytics.
    """
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    session_key = models.CharField(max_length=40, unique=True)
    
    # Session Information
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    device_type = models.CharField(
        max_length=20,
        choices=[
            ('desktop', 'Desktop'),
            ('mobile', 'Mobile'),
            ('tablet', 'Tablet'),
            ('api', 'API Client'),
        ],
        default='desktop'
    )
    
    # Location (approximate based on IP)
    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    
    # Session Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    logout_time = models.DateTimeField(null=True, blank=True)
    
    # Security Flags
    is_suspicious = models.BooleanField(default=False)
    security_score = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=100
    )
    
    class Meta:
        db_table = 'user_sessions'
        verbose_name = 'User Session'
        verbose_name_plural = 'User Sessions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['session_key']),
            models.Index(fields=['ip_address']),
        ]
    
    def __str__(self):
        return f"Session for {self.user.username} from {self.ip_address}"
    
    @property
    def duration(self):
        """Calculate session duration."""
        end_time = self.logout_time or timezone.now()
        return end_time - self.created_at


class AuditLog(models.Model):
    """
    Audit trail for user actions and system events.
    """
    
    ACTION_TYPES = [
        ('login', 'User Login'),
        ('logout', 'User Logout'),
        ('password_change', 'Password Change'),
        ('profile_update', 'Profile Update'),
        ('trade_placed', 'Trade Placed'),
        ('trade_cancelled', 'Trade Cancelled'),
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('settings_change', 'Settings Change'),
        ('security_event', 'Security Event'),
        ('api_access', 'API Access'),
        ('data_export', 'Data Export'),
    ]
    
    user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='audit_logs'
    )
    
    # Event Information
    action_type = models.CharField(max_length=50, choices=ACTION_TYPES)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Request Information
    request_method = models.CharField(max_length=10, blank=True)
    request_path = models.CharField(max_length=500, blank=True)
    request_data = models.JSONField(default=dict, blank=True)
    
    # Response Information
    response_status = models.IntegerField(null=True, blank=True)
    response_data = models.JSONField(default=dict, blank=True)
    
    # Additional Context
    metadata = models.JSONField(default=dict, blank=True)
    risk_level = models.CharField(
        max_length=10,
        choices=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('critical', 'Critical'),
        ],
        default='low'
    )
    
    # Timestamps
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'audit_logs'
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'action_type']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['risk_level']),
            models.Index(fields=['ip_address']),
        ]
    
    def __str__(self):
        user_display = self.user.username if self.user else 'Anonymous'
        return f"{self.action_type} by {user_display} at {self.timestamp}"