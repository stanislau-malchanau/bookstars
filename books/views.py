from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from users.decorators import role_required
from users.mixins import RoleRequiredMixin
from django.views.generic import ListView
from .models import Book

@login_required
def my_books(request):
    # Только для авторизованных пользователей
    books = Book.objects.filter(owner=request.user)
    return render(request, 'books/my_books.html', {'books': books})

@role_required(['admin', 'moderator'])
def moderate_books(request):
    # Только для админов и модераторов
    books = Book.objects.filter(status='moderation')
    return render(request, 'books/moderate_books.html', {'books': books})

class AdminBookListView(RoleRequiredMixin, ListView):
    # Только для админов
    allowed_roles = ['admin']
    model = Book
    template_name = 'books/admin_book_list.html'
    context_object_name = 'books'