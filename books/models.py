from django.db import models
from django.urls import reverse
from django.utils import timezone
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

    MARKETPLACE_CHOICES = [
        ('CA', 'Amazon Canada'),
        ('FR', 'France'),
        ('DE', 'Germany'),
        ('US', 'USA'),
        ('GB', 'UK'),
        ('ES', 'Spain'),
        ('IT', 'Italy'),
        ('NL', 'Netherlands'),
        ('JP', 'Japan'),
        ('MX', 'Mexico'),
        ('BR', 'Brazil'),
        ('ID', 'Indonesia'),
        ('PL', 'Poland'),
        ('AU', 'Australia'),
    ]
    
    preferred_marketplace = models.CharField(
        max_length=2, 
        choices=MARKETPLACE_CHOICES,
        blank=True,
        help_text="Предпочтительный маркетплейс для получения отзывов"
    )

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
    
class BookAssignment(models.Model):
    """Назначение книги читателю для обзора"""
    
    STATUS_CHOICES = [
        ('assigned', 'Assigned'),           # Назначена
        ('reading', 'Reading'),             # В процессе чтения
        ('review_submitted', 'Review Submitted'),  # Отзыв отправлен
        ('completed', 'Completed'),         # Завершено
        ('cancelled', 'Cancelled'),         # Отменено
        ('link_pending', 'Link Pending'),   # Ожидание ссылки на отзыв
    ]
    
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='assignments')
    reader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_books')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='assigned')
    
    # Дата назначения
    assigned_at = models.DateTimeField(default=timezone.now)
    
    # Дата начала чтения
    started_reading_at = models.DateTimeField(null=True, blank=True)
    
    # Дата завершения (отправки отзыва)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Ссылка на отзыв (после завершения)
    review_link = models.URLField(blank=True)
    
    # Награда в звездах
    stars_reward = models.IntegerField(default=100)
    
    # Отслеживание прогресса
    pages_read = models.IntegerField(default=0)
    total_pages = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.reader.username} -> {self.book.title}"
    
    def start_reading(self):
        """Начать чтение книги"""
        self.status = 'reading'
        self.started_reading_at = timezone.now()
        self.save()
    
    def submit_review(self, review_link=""):
        """Отправить отзыв"""
        self.status = 'review_submitted'
        self.review_link = review_link
        self.completed_at = timezone.now()
        self.save()
        
        # Начисляем звезды читателю
        try:
            star_balance = self.reader.star_balance
        except StarBalance.DoesNotExist:
            star_balance = StarBalance.objects.create(user=self.reader)
        
        star_balance.add_stars(self.stars_reward, f"Review submitted for '{self.book.title}'")
    
    def complete_assignment(self):
        """Завершить назначение"""
        self.status = 'completed'
        self.save()
    
    @property
    def is_overdue(self):
        """Проверить, просрочено ли задание"""
        if self.status in ['completed', 'cancelled']:
            return False
        # Задание должно быть завершено в течение 5 дней
        due_date = self.assigned_at + timezone.timedelta(days=5)
        return timezone.now() > due_date
    
    class Meta:
        unique_together = ('book', 'reader')  # Один пользователь не может взять одну книгу дважды
