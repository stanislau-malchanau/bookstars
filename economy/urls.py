from django.urls import path
from . import views

app_name = 'economy'

urlpatterns = [
    path('stars/', views.star_balance, name='star_balance'),
]