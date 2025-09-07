from django.db import models
from users.models import User

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

    def __str__(self):
        return self.title
