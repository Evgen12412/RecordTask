from django.db import models

from django.contrib.auth.models import AbstractUser




class MyUser(AbstractUser):
    email = models.EmailField(unique=True, verbose_name="Адрес электронной почты")
    username = models.CharField(max_length=10, verbose_name="Имя")


    REQUIRED_FIELDS = ['username']  # Добавьте обязательные поля
    USERNAME_FIELD = 'email'  # Укажите поле для аутентификации


    def __str__(self):
        return self.email
