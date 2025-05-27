from django.contrib import admin
from django.utils.html import format_html
from .models import TradeDispute
from django.conf import settings
from django.utils import timezone
import hmac
import hashlib

class TradeDisputeAdmin(admin.ModelAdmin):
    list_display = (
        'id', 
        'trade_link', 
        'resolution_status', 
        'participants', 
        'created_at', 
        'resolved_at',
        'has_evidence'
    )
    list_filter = ('resolution', 'created_at')
    search_fields = ('initiator_token', 'trade__id')
    readonly_fields = (
        'created_at', 
        'resolved_at',
        'trade_link',
        'initiator_token',
        'participants_info'
    )
    ordering = ('-created_at',)
    actions = ['resolve_as_buyer_favored', 'resolve_as_seller_favored', 'resolve_as_split']
    list_per_page = 20
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('trade_link', 'participants_info', 'resolution', 'admin_sig')
        }),
        ('Timing', {
            'fields': ('created_at', 'resolved_at')
        }),
        ('Evidence', {
            'fields': ('evidence_hashes', 'evidence_ipfs_cid')
        }),
    )
    
    def trade_link(self, obj):
        return format_html(
            '<a href="/admin/p2p/p2ptrade/{}/change/">{}</a>',
            obj.trade.id,
            obj.trade.id
        )
    trade_link.short_description = 'Trade'
    
    def resolution_status(self, obj):
        colors = {
            0: 'orange',  # Pending
            1: 'green',   # Buyer
            2: 'red',      # Seller
            3: 'blue',     # Split
        }
        return format_html(
            '<span style="color: {};">{}</span>',
            colors.get(obj.resolution, 'black'),
            obj.get_resolution_display()
        )
    resolution_status.short_description = 'Resolution'
    
    def participants(self, obj):
        hmac_key = settings.XUSDT_SETTINGS['USER_TOKEN_HMAC_KEY'].encode()
        buyer = hmac.new(hmac_key, obj.trade.buyer_token.encode(), hashlib.sha256).hexdigest()[:8]
        seller = hmac.new(hmac_key, obj.trade.seller_token.encode(), hashlib.sha256).hexdigest()[:8]
        return f"B:{buyer} S:{seller}"
    
    def participants_info(self, obj):
        return self.participants(obj)
    participants_info.short_description = 'Participants (truncated)'
    
    def has_evidence(self, obj):
        return bool(obj.evidence_hashes or obj.evidence_ipfs_cid)
    has_evidence.boolean = True
    has_evidence.short_description = 'Evidence?'
    
    def get_readonly_fields(self, request, obj=None):
        if obj and obj.resolution != 0:  # If not pending
            return self.readonly_fields + ('resolution', 'admin_sig')
        return self.readonly_fields
    
    def resolve_as_buyer_favored(self, request, queryset):
        queryset.update(resolution=1, resolved_at=timezone.now())
    resolve_as_buyer_favored.short_description = "Mark as Buyer Favored"
    
    def resolve_as_seller_favored(self, request, queryset):
        queryset.update(resolution=2, resolved_at=timezone.now())
    resolve_as_seller_favored.short_description = "Mark as Seller Favored"
    
    def resolve_as_split(self, request, queryset):
        queryset.update(resolution=3, resolved_at=timezone.now())
    resolve_as_split.short_description = "Mark as Split Funds"
    
    def save_model(self, request, obj, form, change):
        if 'resolution' in form.changed_data and obj.resolution != 0:
            obj.resolved_at = timezone.now()
        super().save_model(request, obj, form, change)

admin.site.register(TradeDispute, TradeDisputeAdmin)