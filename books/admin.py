from django.contrib import admin
from .models import Book

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'status', 'owner', 'created_at']
    list_filter = ['status', 'genre', 'language', 'preferred_marketplace']
    search_fields = ['title', 'author']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'author', 'asin', 'language', 'genre')
        }),
        ('Status & Settings', {
            'fields': ('status', 'reading_type', 'preferred_marketplace')
        }),
        ('Owner & Dates', {
            'fields': ('owner', 'created_at', 'updated_at')
        }),
    )