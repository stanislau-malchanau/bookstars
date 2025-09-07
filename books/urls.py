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
    path('add/', views.add_book_wizard, name='add_book_wizard'),
    path('<int:book_id>/', views.view_book, name='view_book'),
    path('<int:book_id>/edit/', views.edit_book, name='edit_book'),
    path('<int:book_id>/get-reviewed/', views.get_reviewed, name='get_reviewed'),
    path('library/', views.library, name='library'),

    path('assign/<int:book_id>/', views.assign_book, name='assign_book'),
    path('my-assigned-books/', views.my_assigned_books, name='my_assigned_books'),
    path('assignment/<int:assignment_id>/', views.book_for_review, name='book_for_review'),
    path('assignment/<int:assignment_id>/cancel/', views.cancel_assignment, name='cancel_assignment'),
    path('assignment/<int:assignment_id>/report/', views.report_issue, name='report_issue'),

    path('', include('core.urls')), # Пока пусто, но пригодится
]