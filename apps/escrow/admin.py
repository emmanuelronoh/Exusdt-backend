from django.contrib import admin
from .models import EscrowWallet, SystemWallet

class EscrowWalletAdmin(admin.ModelAdmin):
    list_display = ('address', 'user_token', 'created_at', 'last_used')
    search_fields = ('address', 'user_token')
    readonly_fields = ('created_at', 'last_used')
    ordering = ('-created_at',)

class SystemWalletAdmin(admin.ModelAdmin):
    list_display = ('address', 'current_balance', 'collected_fees', 'last_swept_at')
    readonly_fields = ('address', 'current_balance', 'collected_fees')

admin.site.register(EscrowWallet, EscrowWalletAdmin)
admin.site.register(SystemWallet, SystemWalletAdmin)