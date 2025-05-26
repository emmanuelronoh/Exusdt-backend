from django.contrib import admin
from .models import P2PListing, P2PTrade

class P2PListingAdmin(admin.ModelAdmin):
    list_display = ('id', 'usdt_amount', 'fiat_price', 'status', 'created_at')
    list_filter = ('status', 'payment_method')
    search_fields = ('seller_token', 'escrow_address')
    readonly_fields = ('created_at', 'expires_at')
    ordering = ('-created_at',)

class P2PTradeAdmin(admin.ModelAdmin):
    list_display = ('id', 'listing', 'status', 'fee_amount', 'created_at')
    list_filter = ('status',)
    search_fields = ('buyer_token', 'seller_token', 'escrow_tx_hash')
    readonly_fields = ('created_at', 'updated_at', 'completed_at')
    ordering = ('-created_at',)

admin.site.register(P2PListing, P2PListingAdmin)
admin.site.register(P2PTrade, P2PTradeAdmin)