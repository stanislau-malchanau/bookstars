from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.views.generic import ListView
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.paginator import Paginator
from django.db.models import Q, Exists, OuterRef
from django.http import JsonResponse

from users.decorators import role_required
from users.mixins import RoleRequiredMixin

from .models import Book, BookAssignment
from .forms import BookForm, BookCoverForm, BookFileForm, GetReviewedForm

from economy.models import StarBalance

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
        'progress_width': step * 20,
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
        book_data['preferred_marketplace'] = request.POST.get('marketplace', 'US')
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
                status='draft',
                preferred_marketplace=book_data.get('preferred_marketplace', 'US')
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

@login_required
def get_reviewed(request, book_id):
    """Запрос обзоров на книгу"""
    book = get_object_or_404(Book, pk=book_id, owner=request.user)
    
    # Проверяем, что книга в статусе "live"
    if not book.is_live:
        messages.error(request, 'Книгу можно отправить на обзор только в статусе "Live"')
        return redirect('books:view_book', book_id=book.id)
    
    if request.method == 'POST':
        form = GetReviewedForm(request.POST)
        if form.is_valid():
            # Получаем данные из формы
            reading_type = form.cleaned_data['reading_type']
            book_price = form.cleaned_data.get('book_price')
            print_book_link = form.cleaned_data.get('print_book_link')
            print_book_price = form.cleaned_data.get('print_book_price')
            add_goodreads = form.cleaned_data.get('add_goodreads_review')
            goodreads_link = form.cleaned_data.get('goodreads_link')
            add_photo = form.cleaned_data.get('add_photo_review')
            add_video = form.cleaned_data.get('add_video_review')
            
            # Рассчитываем стоимость
            stars_cost = book.get_stars_cost()
            
            # Проверяем баланс звезд
            try:
                star_balance = request.user.star_balance
            except StarBalance.DoesNotExist:
                star_balance = StarBalance.objects.create(user=request.user)
            
            if star_balance.balance < stars_cost:
                messages.error(request, f'Недостаточно звезд. Требуется {stars_cost}, у вас {star_balance.balance}')
                return redirect('books:get_reviewed', book_id=book.id)
            
            # Списываем звезды
            if star_balance.spend_stars(stars_cost, f"Get reviewed for book '{book.title}'"):
                # Обновляем книгу
                book.reading_type = reading_type
                book.book_price = book_price
                book.print_book_link = print_book_link
                book.print_book_price = print_book_price
                book.add_goodreads_review = add_goodreads
                book.goodreads_link = goodreads_link
                book.add_photo_review = add_photo
                book.add_video_review = add_video
                book.stars_cost = stars_cost
                book.review_requested_at = timezone.now()
                book.save()
                
                messages.success(request, f'Запрос на обзор отправлен! Списано {stars_cost} звезд.')
                return redirect('books:my_books')
            else:
                messages.error(request, 'Ошибка при списании звезд')
                return redirect('books:get_reviewed', book_id=book.id)
    else:
        form = GetReviewedForm()
    
    return render(request, 'books/get_reviewed.html', {
        'book': book,
        'form': form,
        'stars_cost': book.get_stars_cost()
    })

@login_required
def library(request):
    """Страница библиотеки книг для обзора"""
    # Получаем только "живые" книги, которые ищут читателей
    books = Book.objects.filter(status='live').select_related('owner')
    
    # Фильтры
    reading_type = request.GET.get('reading_type')
    marketplace = request.GET.get('marketplace')
    language = request.GET.get('language')
    genre = request.GET.get('genre')
    
    if reading_type:
        books = books.filter(reading_type=reading_type)
    if marketplace:
        # Предполагаем, что у Book есть поле preferred_marketplace
        books = books.filter(preferred_marketplace=marketplace)
    if language:
        books = books.filter(language=language)
    if genre:
        books = books.filter(genre=genre)
    
    # Сортировка
    sort_by = request.GET.get('sort', 'created_at')  # по умолчанию новые первыми
    if sort_by == 'stars':
        books = books.order_by('-stars_cost')  #_most stars
    else:
        books = books.order_by('-created_at')
    
    # Добавляем аннотацию: is_assigned — назначена ли книга текущему пользователю
    books = books.annotate(
        is_assigned=Exists(
            BookAssignment.objects.filter(
                book=OuterRef('pk'),
                reader=request.user
            )
        )
    )

    # Пагинация
    paginator = Paginator(books, 12)  # 12 книг на странице
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Получаем уникальные значения для фильтров
    reading_types = Book.READING_TYPES
    languages = Book.objects.filter(status='live').values_list('language', flat=True).distinct()
    genres = Book.objects.filter(status='live').values_list('genre', flat=True).distinct()
    
    context = {
        'page_obj': page_obj,
        'reading_types': reading_types,
        'languages': languages,
        'genres': genres,
        'book_marketplace_choices': Book.MARKETPLACE_CHOICES,
        'current_filters': {
            'reading_type': reading_type,
            'marketplace': marketplace,
            'language': language,
            'genre': genre,
            'sort': sort_by,
        }
    }
    
    return render(request, 'books/library.html', context)

@login_required
def assign_book(request, book_id):
    """Назначить книгу пользователю для обзора"""
    book = get_object_or_404(Book, pk=book_id, status='live')
    
    # Проверяем, не назначен ли уже этот пользователь на эту книгу
    if BookAssignment.objects.filter(book=book, reader=request.user).exists():
        messages.warning(request, 'Вы уже назначены на эту книгу.')
        return redirect('books:library')
    
    # Создаем назначение
    assignment = BookAssignment.objects.create(
        book=book,
        reader=request.user,
        stars_reward=book.get_stars_cost()  # Используем стоимость как награду
    )
    
    messages.success(request, f'Вы успешно назначены на книгу "{book.title}". Начните чтение!')
    return redirect('books:my_assigned_books')

@login_required
def my_assigned_books(request):
    """Страница 'Books I'm Reviewing'"""
    # Получаем назначения текущего пользователя
    assignments = BookAssignment.objects.filter(reader=request.user).select_related('book', 'book__owner')
    
    # Фильтры по статусу
    status_filter = request.GET.get('status')
    if status_filter:
        assignments = assignments.filter(status=status_filter)
    
    # Сортировка
    sort_by = request.GET.get('sort', '-assigned_at')
    assignments = assignments.order_by(sort_by)
    
    # Пагинация
    paginator = Paginator(assignments, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_choices': BookAssignment.STATUS_CHOICES,
        'current_status': status_filter,
    }
    
    return render(request, 'books/my_assigned_books.html', context)

@login_required
def book_for_review(request, assignment_id):
    """Страница деталей книги для обзора"""
    assignment = get_object_or_404(
        BookAssignment, 
        pk=assignment_id, 
        reader=request.user
    )
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'start_reading':
            assignment.start_reading()
            messages.success(request, 'Вы начали чтение книги!')
            
        elif action == 'submit_review':
            review_link = request.POST.get('review_link', '')
            assignment.submit_review(review_link)
            messages.success(request, 'Отзыв отправлен! Вам начислены звезды.')
            
        elif action == 'complete':
            assignment.complete_assignment()
            messages.success(request, 'Назначение завершено.')
            
        return redirect('books:book_for_review', assignment_id=assignment.id)
    
    return render(request, 'books/book_for_review.html', {
        'assignment': assignment,
    })

@login_required
def cancel_assignment(request, assignment_id):
    """Отменить назначение"""
    assignment = get_object_or_404(
        BookAssignment, 
        pk=assignment_id, 
        reader=request.user
    )
    
    if request.method == 'POST':
        assignment.status = 'cancelled'
        assignment.save()
        messages.success(request, 'Назначение отменено.')
        return redirect('books:my_assigned_books')
    
    return render(request, 'books/cancel_assignment.html', {
        'assignment': assignment,
    })

@login_required
def report_issue(request, assignment_id):
    """Сообщить о проблеме с книгой"""
    assignment = get_object_or_404(
        BookAssignment, 
        pk=assignment_id, 
        reader=request.user
    )
    
    if request.method == 'POST':
        issue_type = request.POST.get('issue_type')
        message = request.POST.get('message', '')
        
        # Здесь можно добавить логику отправки уведомления админу
        # Пока просто показываем сообщение
        messages.success(request, 'Сообщение отправлено администратору.')
        return redirect('books:book_for_review', assignment_id=assignment.id)
    
    return render(request, 'books/report_issue.html', {
        'assignment': assignment,
        'issue_types': [
            ('broken_link', 'Broken link'),
            ('wrong_price', 'Wrong price'),
            ('wrong_book', 'Wrong book'),
            ('pdf_file_issue', 'PDF file issue'),
            ('other', 'Other'),
        ]
    })