from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import (
    SwapToken, SwapRoute, SwapQuote,
    SwapTransaction, SwapAllowance,
    SwapPrice, MarketStats
)

@admin.register(SwapToken)
class SwapTokenAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'name', 'network', 'is_active', 'min_swap_amount')
    list_filter = ('network', 'is_active')
    search_fields = ('symbol', 'name', 'contract_address')
    readonly_fields = ('symbol', 'decimals')
    fieldsets = (
        (None, {
            'fields': ('symbol', 'name', 'network')
        }),
        ('Details', {
            'fields': ('contract_address', 'decimals', 'logo_url')
        }),
        ('Settings', {
            'fields': ('is_active', 'min_swap_amount')
        }),
    )

@admin.register(SwapRoute)
class SwapRouteAdmin(admin.ModelAdmin):
    list_display = ('id', 'token_in', 'token_out', 'fee_percentage', 'is_active')
    list_filter = ('is_active', 'token_in__network', 'token_out__network')
    search_fields = ('token_in__symbol', 'token_out__symbol')
    autocomplete_fields = ('token_in', 'token_out')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('token_in', 'token_out')

@admin.register(SwapQuote)
class SwapQuoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'token_in', 'token_out', 'amount_in', 'amount_out', 'valid_until')
    list_filter = ('token_in__network', 'token_out__network')
    search_fields = ('token_in__symbol', 'token_out__symbol')
    readonly_fields = ('id', 'created_at')
    date_hierarchy = 'created_at'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('token_in', 'token_out')

@admin.register(SwapTransaction)
class SwapTransactionAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'status', 'from_address_short',
        'to_address_short', 'created_at', 'execution_time'
    )
    list_filter = ('status', 'quote__token_in__network')
    search_fields = ('from_address', 'to_address', 'tx_hash')
    readonly_fields = ('id', 'created_at', 'executed_at', 'completed_at')
    date_hierarchy = 'created_at'
    actions = ['mark_as_completed']

    def from_address_short(self, obj):
        return f"{obj.from_address[:6]}...{obj.from_address[-4:]}"
    from_address_short.short_description = 'From'

    def to_address_short(self, obj):
        return f"{obj.to_address[:6]}...{obj.to_address[-4:]}"
    to_address_short.short_description = 'To'

    def execution_time(self, obj):
        if obj.executed_at and obj.completed_at:
            return obj.completed_at - obj.executed_at
        return None
    execution_time.short_description = 'Execution Time'

    def mark_as_completed(self, request, queryset):
        updated = queryset.filter(status='pending').update(
            status='completed',
            completed_at=timezone.now()
        )
        self.message_user(request, f"{updated} transactions marked as completed")
    mark_as_completed.short_description = "Mark selected as completed"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('quote__token_in', 'quote__token_out')

@admin.register(SwapAllowance)
class SwapAllowanceAdmin(admin.ModelAdmin):
    list_display = ('token', 'contract_address_short', 'allowance_amount', 'last_updated')
    search_fields = ('token__symbol', 'contract_address', 'user_token')
    readonly_fields = ('last_updated',)

    def contract_address_short(self, obj):
        return f"{obj.contract_address[:6]}...{obj.contract_address[-4:]}"
    contract_address_short.short_description = 'Contract'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('token')

@admin.register(SwapPrice)
class SwapPriceAdmin(admin.ModelAdmin):
    list_display = ('token', 'price_usd', 'timestamp')
    list_filter = ('token__network',)
    search_fields = ('token__symbol',)
    readonly_fields = ('timestamp',)
    date_hierarchy = 'timestamp'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('token')

@admin.register(MarketStats)
class MarketStatsAdmin(admin.ModelAdmin):
    list_display = ('token_pair', 'volume_24h', 'change_24h', 'last_updated')
    search_fields = ('token_pair',)
    readonly_fields = ('last_updated',)
    list_editable = ('volume_24h', 'change_24h')