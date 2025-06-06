from django.contrib import admin
from django.utils.html import format_html
from .models import P2PListing, P2PTrade

@admin.register(P2PListing)
class P2PListingAdmin(admin.ModelAdmin):
    list_display = (
        'id_short',
        'get_crypto_display',
        'get_fiat_display',
        'payment_method_display',
        'status_display',
        'created_at_short',
        'expires_at_short',
        'is_active'
    )
    list_filter = (
        'status',
        'crypto_type',
        'payment_method',
        'created_at',
    )
    search_fields = (
        'seller_token',
        'description',
        'id',
    )
    readonly_fields = (
        'id',
        'created_at',
        'expires_at',
        'seller_token',
        'status',
        'crypto_details',
        'fiat_details',
        'time_details',
    )
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'id',
                'seller_token',
                'status',
            )
        }),
        ('Trade Details', {
            'fields': (
                'crypto_details',
                'fiat_details',
            )
        }),
        ('Payment Information', {
            'fields': (
                'payment_method',
                'description',
                'instructions_enc',
            )
        }),
        ('Timestamps', {
            'fields': (
                'time_details',
            )
        }),
    )
    ordering = ('-created_at',)
    list_per_page = 20

    def id_short(self, obj):
        return str(obj.id)[:8] + "..."
    id_short.short_description = "ID"

    def get_crypto_display(self, obj):
        return f"{obj.crypto_amount} {obj.crypto_currency} ({obj.get_crypto_type_display()})"
    get_crypto_display.short_description = "Crypto"

    def get_fiat_display(self, obj):
        return f"{obj.fiat_amount} {obj.fiat_currency}"
    get_fiat_display.short_description = "Fiat"

    def payment_method_display(self, obj):
        return obj.get_payment_method_display()
    payment_method_display.short_description = "Payment Method"

    def status_display(self, obj):
        status_map = {
            1: ('green', 'Active'),
            2: ('blue', 'Funded'),
            3: ('orange', 'Reserved'),
            4: ('gray', 'Completed'),
            5: ('red', 'Expired'),
        }
        color, text = status_map.get(obj.status, ('black', 'Unknown'))
        return format_html(
            '<span style="color: {};">{}</span>',
            color,
            text
        )
    status_display.short_description = "Status"

    def created_at_short(self, obj):
        return obj.created_at.strftime("%Y-%m-%d %H:%M")
    created_at_short.short_description = "Created"

    def expires_at_short(self, obj):
        return obj.expires_at.strftime("%Y-%m-%d %H:%M")
    expires_at_short.short_description = "Expires"

    def is_active(self, obj):
        return obj.expires_at > timezone.now()
    is_active.boolean = True
    is_active.short_description = "Active"

    def crypto_details(self, obj):
        return format_html(
            "Type: {}<br>Currency: {}<br>Amount: {}",
            obj.get_crypto_type_display(),
            obj.crypto_currency,
            obj.crypto_amount
        )
    crypto_details.short_description = "Crypto Details"

    def fiat_details(self, obj):
        return format_html(
            "Currency: {}<br>Amount: {}",
            obj.fiat_currency,
            obj.fiat_amount
        )
    fiat_details.short_description = "Fiat Details"

    def time_details(self, obj):
        return format_html(
            "Created: {}<br>Expires: {}",
            obj.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            obj.expires_at.strftime("%Y-%m-%d %H:%M:%S")
        )
    time_details.short_description = "Timestamps"

@admin.register(P2PTrade)
class P2PTradeAdmin(admin.ModelAdmin):
    list_display = (
        'id_short',
        'listing_link',
        'status_display',
        'fee_amount',
        'created_at_short',
        'updated_at_short',
        'completed_at_short',
    )
    list_filter = (
        'status',
        'created_at',
        'completed_at',
    )
    search_fields = (
        'buyer_token',
        'seller_token',
        'escrow_tx_hash',
        'payment_proof_hash',
        'listing__id',
    )
    readonly_fields = (
        'id',
        'created_at',
        'updated_at',
        'completed_at',
        'buyer_token',
        'seller_token',
        'trade_details',
        'status_history',
    )
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'id',
                'listing',
                'status',
            )
        }),
        ('Parties', {
            'fields': (
                'buyer_token',
                'seller_token',
            )
        }),
        ('Transaction Details', {
            'fields': (
                'escrow_tx_hash',
                'payment_proof_hash',
                'fee_amount',
            )
        }),
        ('Trade Details', {
            'fields': (
                'trade_details',
                'status_history',
            )
        }),
    )
    ordering = ('-created_at',)
    list_per_page = 20

    def id_short(self, obj):
        return str(obj.id)[:8] + "..."
    id_short.short_description = "ID"

    def listing_link(self, obj):
        url = reverse("admin:p2p_p2plisting_change", args=[obj.listing.id])
        return format_html('<a href="{}">{}</a>', url, str(obj.listing.id)[:8] + "...")
    listing_link.short_description = "Listing"

    def status_display(self, obj):
        status_map = {
            0: ('gray', 'Created'),
            1: ('blue', 'Funded'),
            2: ('orange', 'Payment Sent'),
            3: ('green', 'Completed'),
            4: ('red', 'Disputed'),
            5: ('black', 'Canceled'),
        }
        color, text = status_map.get(obj.status, ('black', 'Unknown'))
        return format_html(
            '<span style="color: {};">{}</span>',
            color,
            text
        )
    status_display.short_description = "Status"

    def created_at_short(self, obj):
        return obj.created_at.strftime("%Y-%m-%d %H:%M")
    created_at_short.short_description = "Created"

    def updated_at_short(self, obj):
        return obj.updated_at.strftime("%Y-%m-%d %H:%M") if obj.updated_at else "-"
    updated_at_short.short_description = "Updated"

    def completed_at_short(self, obj):
        return obj.completed_at.strftime("%Y-%m-%d %H:%M") if obj.completed_at else "-"
    completed_at_short.short_description = "Completed"

    def trade_details(self, obj):
        return format_html(
            "USDT Amount: {}<br>Fee Amount: {}<br>Escrow TX: {}<br>Payment Proof: {}",
            obj.fiat_amount,
            obj.fee_amount,
            obj.escrow_tx_hash or "-",
            obj.payment_proof_hash or "-"
        )
    trade_details.short_description = "Trade Details"

    def status_history(self, obj):
        return format_html(
            "Created: {}<br>Updated: {}<br>Completed: {}",
            obj.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            obj.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
            obj.completed_at.strftime("%Y-%m-%d %H:%M:%S") if obj.completed_at else "-"
        )
    status_history.short_description = "Status History"