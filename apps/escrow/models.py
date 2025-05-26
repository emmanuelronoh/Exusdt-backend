import uuid
import hmac
import hashlib
from django.db import models
from django.conf import settings
from django.utils import timezone


class EscrowWallet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    address = models.CharField(
        max_length=42,
        unique=True,
        help_text="ETH address"
    )
    user_token = models.CharField(
        max_length=64,
        help_text="HMAC-SHA256(user_identity)"
    )
    balance_commitment = models.CharField(
        max_length=64,
        help_text="SHA3-256(balance+salt)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['address'], name='idx_escrow_address'),
            models.Index(fields=['user_token'], name='idx_escrow_user'),
        ]

    def __str__(self):
        return f"Escrow {self.address}"

    @classmethod
    def generate_user_token(cls, client_token):
        """Generate HMAC-SHA256 user token from client token"""
        hmac_key = settings.XUSDT_SETTINGS['USER_TOKEN_HMAC_KEY'].encode()
        return hmac.new(hmac_key, client_token.encode(), hashlib.sha256).hexdigest()


class SystemWallet(models.Model):
    address = models.CharField(
        max_length=42,
        primary_key=True,
        help_text="ETH address"
    )
    private_key_enc = models.TextField(
        help_text="Age-encrypted private key"
    )
    current_balance = models.DecimalField(
        max_digits=20,
        decimal_places=6,
        default=0
    )
    collected_fees = models.DecimalField(
        max_digits=20,
        decimal_places=6,
        default=0
    )
    last_swept_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['current_balance'], name='idx_wallet_balance'),
        ]

    def __str__(self):
        return f"System Wallet {self.address}"