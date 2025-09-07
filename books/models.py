from django.db import models
from users.models import User
import os

def book_cover_upload_path(instance, filename):
    """Путь для сохранения обложки книги"""
    return f'books/covers/{instance.owner.id}/{instance.id or "temp"}/{filename}'

def book_file_upload_path(instance, filename):
    """Путь для сохранения файла книги"""
    return f'books/files/{instance.owner.id}/{instance.id or "temp"}/{filename}'

class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    asin = models.CharField(max_length=20, blank=True, null=True)
    language = models.CharField(max_length=50)
    genre = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=[
        ('draft', 'Draft'),
        ('moderation', 'Moderation'),
        ('live', 'Live'),
        ('rejected', 'Rejected'),
    ], default='draft')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='books')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    cover_image = models.ImageField(
        upload_to=book_cover_upload_path,
        blank=True,
        null=True,
        help_text="Загрузите обложку книги"
    )

    book_file = models.FileField(
        upload_to=book_file_upload_path,
        blank=True,
        null=True,
        help_text="Загрузите файл книги (PDF, EPUB, DOC, DOCX)"
    )

    def __str__(self):
        return self.title
