from django.contrib import admin
from .models import TradeDispute

class TradeDisputeAdmin(admin.ModelAdmin):
    list_display = ('id', 'trade', 'resolution', 'created_at', 'resolved_at')
    list_filter = ('resolution',)
    search_fields = ('initiator_token', 'trade__id')
    readonly_fields = ('created_at', 'resolved_at')
    ordering = ('-created_at',)

admin.site.register(TradeDispute, TradeDisputeAdmin)