from django.db import models
from django.urls import reverse
from users.models import User
import os

def book_cover_upload_path(instance, filename):
    """Путь для сохранения обложки книги"""
    return f'books/covers/{instance.owner.id}/{instance.id or "temp"}/{filename}'

def book_file_upload_path(instance, filename):
    """Путь для сохранения файла книги"""
    return f'books/files/{instance.owner.id}/{instance.id or "temp"}/{filename}'

class Book(models.Model):
    READING_TYPES = [
        ('standard', 'Standard'),
        ('kindle_unlimited', 'Kindle Unlimited'),
        ('verified_ebook', 'Verified Purchase (eBook)'),
        ('verified_print', 'Verified Print Copy'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('moderation', 'Moderation'),
        ('live', 'Live'),
        ('rejected', 'Rejected'),
        ('canceled', 'Canceled'),
    ]

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

    reading_type = models.CharField(max_length=20, choices=READING_TYPES, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Поля для разных типов чтения
    book_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    print_book_link = models.URLField(null=True, blank=True)
    print_book_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Goodreads
    goodreads_link = models.URLField(blank=True)
    add_goodreads_review = models.BooleanField(default=False)
    
    # Фото/видео в отзывах (для Verified Print)
    add_photo_review = models.BooleanField(default=False)
    add_video_review = models.BooleanField(default=False)
    
    # Стоимость в звездах для получения обзоров
    stars_cost = models.IntegerField(default=0, help_text="Количество звезд, необходимых для получения обзоров")
    
    # Дата активации получения обзоров
    review_requested_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('books:view_book', kwargs={'book_id': self.pk})
    
    def get_stars_cost(self):
        """Рассчитать стоимость в звездах в зависимости от типа чтения"""
        costs = {
            'standard': 100,
            'kindle_unlimited': 150,
            'verified_ebook': 200,
            'verified_print': 250,
        }
        return costs.get(self.reading_type, 100)
    
    @property
    def is_live(self):
        return self.status == 'live'
