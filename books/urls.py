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
    path('', include('core.urls')), # Пока пусто, но пригодится
]