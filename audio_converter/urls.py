from django.urls import path

from .views import *

urlpatterns = [
    path('record/', Record.as_view(), name='record')
]