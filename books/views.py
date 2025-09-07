from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.http import JsonResponse

from users.decorators import role_required
from users.mixins import RoleRequiredMixin

from .models import Book
from .forms import BookForm, BookCoverForm, BookFileForm

import json
import os

@login_required
def my_books(request):
    # Только для авторизованных пользователей
    books = Book.objects.filter(owner=request.user)
    return render(request, 'books/my_books.html', {'books': books})

# @login_required
# def add_book(request):
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

# Структура шагов добавления книги
BOOK_ADD_STEPS = {
    1: {'title': 'New Book', 'template': 'books/add_book_step1.html'},
    2: {'title': 'Choose Your Readers', 'template': 'books/add_book_step2.html'},
    3: {'title': 'Add the Front Cover', 'template': 'books/add_book_step3.html'},
    4: {'title': 'Point us to your book on Amazon', 'template': 'books/add_book_step4.html'},
    5: {'title': 'Submit last information', 'template': 'books/add_book_step5.html'},
}

@login_required
def add_book_wizard(request):
    # Инициализация сессии для данных книги
    if 'book_data' not in request.session:
        request.session['book_data'] = {}
    
    step = int(request.GET.get('step', 1))
    
    # Ограничение шагов
    if step < 1 or step > len(BOOK_ADD_STEPS):
        step = 1
    
    # Обработка POST запроса
    if request.method == 'POST':
        return handle_step_post(request, step)
    
    # Отображение формы
    context = {
        'step': step,
        'total_steps': len(BOOK_ADD_STEPS),
        'step_title': BOOK_ADD_STEPS[step]['title'],
        'book_data': request.session.get('book_data', {}),
    }
    
    return render(request, BOOK_ADD_STEPS[step]['template'], context)

def handle_step_post(request, step):
    book_data = request.session.get('book_data', {})
    
    if step == 1:
        # Шаг 1: Основная информация о книге
        book_data['title'] = request.POST.get('title', '')
        book_data['author'] = request.POST.get('author', '')
        book_data['asin'] = request.POST.get('asin', '')
        
    elif step == 2:
        # Шаг 2: Выбор типа чтения и загрузка файла
        book_data['reading_type'] = request.POST.get('reading_type', '')
        
        # Обработка загрузки файла
        form = BookFileForm(request.POST, request.FILES)
        if form.is_valid():
            book_file = request.FILES.get('book_file')
            if book_file:
                book_data['book_file_name'] = book_file.name
                book_data['has_book_file'] = True
        else:
            # Добавляем ошибки формы в messages
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
            return redirect(f"{request.path}?step=2")
        
    elif step == 3:
        # Шаг 3: Загрузка обложки
        form = BookCoverForm(request.POST, request.FILES)
        if form.is_valid():
            cover_file = request.FILES.get('cover_image')
            if cover_file:
                # Сохраняем файл временно в сессию или на диск
                # Для простоты сохраним путь к файлу в сессии
                book_data['cover_image_name'] = cover_file.name
                # Файл будет сохранен позже при создании книги
                # Пока просто отметим, что обложка загружена
                book_data['has_cover'] = True
        else:
            messages.error(request, 'Ошибка при загрузке обложки')
            return redirect(f"{request.path}?step=3")
        
    elif step == 4:
        # Шаг 4: Информация о книге на Amazon
        book_data['amazon_url'] = request.POST.get('amazon_url', '')
        book_data['language'] = request.POST.get('language', 'English')
        book_data['marketplace'] = request.POST.get('marketplace', 'USA')
        book_data['goodreads_link'] = request.POST.get('goodreads_link', '')
        book_data['genre'] = request.POST.get('genre', '')
        
    elif step == 5:
        # Шаг 5: Финальная информация и сохранение
        book_data['word_count'] = request.POST.get('word_count', '')
        book_data['summary'] = request.POST.get('summary', '')
        book_data['author_info'] = request.POST.get('author_info', '')
        
        # Сохранение книги в базу
        try:
            book = Book.objects.create(
                title=book_data['title'],
                author=book_data['author'],
                asin=book_data['asin'] or None,
                language=book_data['language'],
                genre=book_data['genre'],
                owner=request.user,
                status='draft'
            )
            
            # Если была загружена обложка, сохраняем её
            if 'cover_image_name' in book_data and request.FILES.get('cover_image'):
                cover_file = request.FILES['cover_image']
                book.cover_image.save(
                    book_data['cover_image_name'],
                    cover_file,
                    save=True
                )
            
            # Если был загружен файл книги, сохраняем его
            if 'book_file_name' in book_data and request.FILES.get('book_file'):
                book_file = request.FILES['book_file']
                book.book_file.save(
                    book_data['book_file_name'],
                    book_file,
                    save=True
                )
            
            # Очищаем сессию
            del request.session['book_data']
            messages.success(request, 'Книга успешно добавлена и отправлена на модерацию!')
            return redirect('books:my_books')
        except Exception as e:
            messages.error(request, f'Ошибка при сохранении книги: {str(e)}')
            return redirect('books:add_book_wizard')
    
    # Сохраняем данные в сессию
    request.session['book_data'] = book_data
    request.session.modified = True
    
    # Переход к следующему шагу
    next_step = min(step + 1, len(BOOK_ADD_STEPS))
    return redirect(f"{request.path}?step={next_step}")

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