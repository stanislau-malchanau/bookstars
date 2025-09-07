from django.contrib import admin
from django.urls import path, include
from . import views

app_name = 'books'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('users.urls')),
    path('my-books/', views.my_books, name='my_books'),
    path('moderate/', views.moderate_books, name='moderate_books'),
    path('admin-list/', views.AdminBookListView.as_view(), name='admin_book_list'),
    # path('add/', views.add_book, name='add_book'),
    path('add/', views.add_book_wizard, name='add_book_wizard'),
    path('<int:book_id>/', views.view_book, name='view_book'),
    path('<int:book_id>/get-reviewed/', views.get_reviewed, name='get_reviewed'),
    path('library/', views.library, name='library'),
    path('', include('core.urls')), # Пока пусто, но пригодится
]