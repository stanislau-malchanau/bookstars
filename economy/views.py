from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import StarBalance, StarTransaction

@login_required
def star_balance(request):
    """Отображение баланса звезд пользователя"""
    try:
        balance = request.user.star_balance
    except StarBalance.DoesNotExist:
        balance = StarBalance.objects.create(user=request.user)
    
    # Получаем последние транзакции
    transactions = StarTransaction.objects.filter(user=request.user).order_by('-created_at')[:10]
    
    return render(request, 'economy/star_balance.html', {
        'balance': balance,
        'transactions': transactions
    })