# core/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import AnonymousUser, SecurityEvent

class AnonymousUserAdmin(UserAdmin):
    model = AnonymousUser

    list_display = ('exchange_code', 'trust_score', 'last_active', 'created_at')
    list_filter = ('trust_score', 'is_active')
    search_fields = ('exchange_code',)
    ordering = ('-created_at',)
    
    # Make all security-related fields read-only
    readonly_fields = (
        'exchange_code', 
        'client_token',
        'session_salt',
        'password_hash',
        'created_at',
        'last_active',
        'deleted_at'
    )

    fieldsets = (
        (None, {'fields': ('exchange_code', 'trust_score', 'is_active')}),
        ('Timestamps', {'fields': ('created_at', 'last_active', 'deleted_at')}),
        ('Security Information', {
            'fields': ('client_token', 'session_salt', 'password_hash'),
            'classes': ('collapse',)  # Makes this section collapsible
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('exchange_code', 'password1', 'password2', 'trust_score'),
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        """Ensure all security fields remain read-only"""
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if obj:  # Editing an existing user
            readonly_fields.extend(['exchange_code', 'client_token', 'session_salt'])
        return readonly_fields

    def save_model(self, request, obj, form, change):
        """Handle password changes properly"""
        if 'password1' in form.data:
            obj.set_password(form.data['password1'])
        super().save_model(request, obj, form, change)

class SecurityEventAdmin(admin.ModelAdmin):
    list_display = ('event_type', 'actor_token', 'created_at')
    list_filter = ('event_type',)
    search_fields = ('actor_token',)
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)

admin.site.register(AnonymousUser, AnonymousUserAdmin)
admin.site.register(SecurityEvent, SecurityEventAdmin)