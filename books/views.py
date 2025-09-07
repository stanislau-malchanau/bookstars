from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from users.decorators import role_required
from users.mixins import RoleRequiredMixin
from django.views.generic import ListView
from .models import Book
from .forms import BookForm

@login_required
def my_books(request):
    # Только для авторизованных пользователей
    books = Book.objects.filter(owner=request.user)
    return render(request, 'books/my_books.html', {'books': books})

@login_required
def add_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            book = form.save(commit=False)
            book.owner = request.user
            book.status = 'draft'  # Новая книга в статусе черновика
            book.save()
            messages.success(request, 'Книга успешно добавлена!')
            return redirect('books:my_books')
    else:
        form = BookForm()
    
    return render(request, 'books/add_book.html', {'form': form})

@login_required
def view_book(request, book_id):
    book = get_object_or_404(Book, pk=book_id, owner=request.user)
    return render(request, 'books/view_book.html', {'book': book})

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