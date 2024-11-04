from django.contrib.auth.decorators import login_required
from rest_framework.generics import get_object_or_404

from .user_login import UserLogIn
from .user_register import UserRegister
from django.contrib.auth import login, logout, authenticate
from .models import MyUser
from django.shortcuts import render, redirect
import logging
from django.http import Http404
from django.utils.translation import gettext as _

from text_processing.models import Transcription

logger = logging.getLogger(__name__)


# Create your views here.

@login_required
def home(request, user_id):
    try:
        # Получаем пользователя
        user = get_object_or_404(MyUser, id=user_id)

        # Получаем все задачи (транскрипции) для пользователя
        tasks = Transcription.objects.filter(user=user)

        # Проверяем, имеет ли пользователь право просматривать каждую задачу
        for task in tasks:
            if task.record and task.record.user != user:
                logger.warning(f"User {request.user.id} tried to access task {task.id} of user {user_id}")
                raise Http404(_("You do not have permission to view this task."))

        # Рендерим шаблон с данными пользователя и задач
        return render(request, 'home.html', {'user': user, 'tasks': tasks})

    except Http404 as e:
        logger.error(f"Http404 error: {e}")
        raise
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise Http404(_("An error occurred while processing your request."))

def register(request):
    if request.method == 'POST':
        form = UserRegister(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            # Создание пользователя
            user = MyUser(email=email, username=username)
            user.set_password(password)
            user.save()

            return redirect('home', user_id = user.id)
    else:
        form = UserRegister()

    login_form = UserLogIn()
    return render(request, 'auth.html', {'registration_form': form, 'login_form': login_form})

def user_login(request):
    if request.method == 'POST':
        form = UserLogIn(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # Аутентификация пользователя
            user = authenticate(request, email=email, password=password)
            logger.debug("Authenticated user: %s", user)
            if user is not None:
                # Логин пользователя
                login(request, user)
                logger.debug("User logged in: %s", user)
                return redirect('home', user_id = user.id)
            else:
                form.add_error(None, 'Неверный email или пароль')
                logger.debug("Authentication failed")
    else:
        form = UserLogIn()

    registration_form = UserRegister()
    return render(request, 'auth.html', {'login_form': form, 'registration_form': registration_form})

def logout_user(request):
    logout(request)
    return redirect('login')

