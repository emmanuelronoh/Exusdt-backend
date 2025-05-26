import uuid
from django.db import models
from django.utils import timezone
from django.conf import settings


class TradeDispute(models.Model):
    RESOLUTION_CHOICES = (
        (0, 'Pending'),
        (1, 'BuyerFavored'),
        (2, 'SellerFavored'),
        (3, 'SplitFunds'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    trade = models.OneToOneField(
        'p2p.P2PTrade',
        on_delete=models.CASCADE,
        related_name='dispute'
    )
    initiator_token = models.CharField(max_length=64)
    evidence_hashes = models.TextField(
        null=True,
        blank=True,
        help_text="Array of SHA3-256(evidence_files)"
    )
    resolution = models.SmallIntegerField(
        choices=RESOLUTION_CHOICES,
        default=0,
        help_text="0=Pending,1=BuyerFavored,2=SellerFavored,3=SplitFunds"
    )
    admin_sig = models.CharField(
        max_length=96,
        null=True,
        blank=True,
        help_text="Ed25519 signature of resolution"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['trade'], name='idx_dispute_trade'),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"Dispute for Trade {self.trade_id} - {self.get_resolution_display()}"