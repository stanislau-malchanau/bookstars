from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('moderator', 'Moderator'),
        ('author', 'Author'),
        ('reader', 'Reader'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='author')
