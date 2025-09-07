from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def my_books(request):
    # Пока просто заглушка
    return render(request, 'books/my_books.html')