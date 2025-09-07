from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('users.urls')),
    path('', include('core.urls')), # Пока пусто, но пригодится
]

app_name = 'books'

urlpatterns = [
    path('my-books/', views.my_books, name='my_books'),
]