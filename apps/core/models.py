import uuid
import hashlib
import hmac
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings


class AnonymousUserManager(BaseUserManager):
    def create_user(self, exchange_code, password, **extra_fields):
        if not exchange_code:
            raise ValueError('The Exchange Code must be set')
        
        user = self.model(
            exchange_code=exchange_code,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    
    def create_superuser(self, exchange_code, password, **extra_fields):
        extra_fields.setdefault('trust_score', 100)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(exchange_code, password, **extra_fields)



class AnonymousUser(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    exchange_code = models.CharField(
        max_length=8,
        unique=True,
        editable=False,
        help_text="Public identifier (EX-1234)"
    )
    password_hash = models.CharField(max_length=255, editable=False)
    session_salt = models.CharField(max_length=32, editable=False)
    client_token = models.CharField(
        max_length=64,
        unique=True,
        editable=False,
        help_text="SHA3-256(salt + password_hash)"
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    last_active = models.DateTimeField(null=True, blank=True)
    trust_score = models.SmallIntegerField(
        default=100,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="0-100 reputation score"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = 'exchange_code'
    REQUIRED_FIELDS = []

    objects = AnonymousUserManager()

    def __str__(self):
        return f"User {self.exchange_code}"

    def set_password(self, raw_password):
        """Create password hash and client token"""
        # Generate password hash (handled by Django's AbstractBaseUser)
        super().set_password(raw_password)
        
        # Generate new session salt
        self.session_salt = hashlib.sha256(uuid.uuid4().bytes).hexdigest()[:32]
        
        # Generate client token
        token_data = f"{self.session_salt}{self.password_hash}".encode()
        self.client_token = hashlib.sha3_256(token_data).hexdigest()
        
        # Update last active time
        self.last_active = timezone.now()

    def rotate_session_salt(self):
        """Rotate session salt on login"""
        self.session_salt = hashlib.sha256(uuid.uuid4().bytes).hexdigest()[:32]
        self.save()

    class Meta:
        indexes = [
            models.Index(fields=['exchange_code'], name='idx_user_exchange_code'),
            models.Index(fields=['client_token'], name='idx_user_client_token'),
        ]


class SecurityEvent(models.Model):
    EVENT_TYPES = (
        (1, 'Login'),
        (2, 'Trade'),
        (3, 'Dispute'),
        (4, 'Admin'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_type = models.SmallIntegerField(choices=EVENT_TYPES)
    actor_token = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        help_text="HMAC-SHA256(actor_identity)"
    )
    ip_hmac = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        help_text="HMAC-SHA256(ip_address)"
    )
    details_enc = models.TextField(
        null=True,
        blank=True,
        help_text="Age-encrypted details"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['event_type'], name='idx_event_type'),
            models.Index(fields=['actor_token'], name='idx_event_actor'),
            models.Index(fields=['created_at'], name='idx_event_timestamp'),
        ]

    def __str__(self):
        return f"{self.get_event_type_display()} event at {self.created_at}"