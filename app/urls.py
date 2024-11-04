
from django.contrib import admin
from django.urls import path, include

from . import views

urlpatterns = [
    path('home/<int:user_id>/', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('', views.user_login, name='login'),  # Используем views.user_login вместо views.login
    path('logout/', views.logout_user, name='logout'),
]