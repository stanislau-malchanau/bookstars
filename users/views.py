from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm
from economy.models import StarBalance

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Автоматический логин после регистрации

            # Добавляем бонусные звезды при регистрации
            try:
                star_balance = user.star_balance
            except StarBalance.DoesNotExist:
                star_balance = StarBalance.objects.create(user=user)
            
            # Бонус 2000 звезд при регистрации (как в тарифе)
            star_balance.add_stars(2000, "Signup bonus")

            return redirect('core:home')  # Перенаправление на главную (пока заглушка)
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})