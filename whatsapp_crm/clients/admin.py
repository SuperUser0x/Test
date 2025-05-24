from django.contrib import admin
from .models import Client

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone_number', 'email', 'status', 'owner', 'created_at', 'updated_at')
    list_filter = ('status', 'owner', 'created_at')
    search_fields = ('name', 'phone_number', 'email', 'notes')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

    fieldsets = (
        (None, {
            'fields': ('name', 'phone_number', 'email', 'status', 'owner')
        }),
        ('Additional Information', {
            'classes': ('collapse',),
            'fields': ('notes',),
        }),
    )
    readonly_fields = ('created_at', 'updated_at')
