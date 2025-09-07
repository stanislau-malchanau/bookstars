from django.contrib import admin
from .models import Book

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'status', 'owner', 'created_at']
    list_filter = ['status', 'genre', 'language']
