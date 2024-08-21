from django.urls import path
from app_pages import views

urlPatterns = [
    path('', views.home, name='home'),
]