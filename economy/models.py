from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class StarBalance(models.Model):
    """Баланс звезд пользователя"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='star_balance')
    balance = models.IntegerField(default=0, help_text="Текущий баланс звезд")
    total_earned = models.IntegerField(default=0, help_text="Всего заработано звезд")
    total_spent = models.IntegerField(default=0, help_text="Всего потрачено звезд")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}: {self.balance} stars"

    def add_stars(self, amount, reason=""):
        """Добавить звезды пользователю"""
        self.balance += amount
        self.total_earned += amount
        self.save()
        # Логируем операцию
        StarTransaction.objects.create(
            user=self.user,
            amount=amount,
            transaction_type='earned',
            reason=reason
        )

    def spend_stars(self, amount, reason=""):
        """Потратить звезды"""
        if self.balance >= amount:
            self.balance -= amount
            self.total_spent += amount
            self.save()
            # Логируем операцию
            StarTransaction.objects.create(
                user=self.user,
                amount=amount,
                transaction_type='spent',
                reason=reason
            )
            return True
        return False

class StarTransaction(models.Model):
    """История транзакций звезд"""
    TRANSACTION_TYPES = [
        ('earned', 'Earned'),
        ('spent', 'Spent'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='star_transactions')
    amount = models.IntegerField()
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    reason = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} {self.transaction_type} {self.amount} stars"

# Сигнал для автоматического создания баланса при создании пользователя
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_star_balance(sender, instance, created, **kwargs):
    if created:
        StarBalance.objects.create(user=instance)