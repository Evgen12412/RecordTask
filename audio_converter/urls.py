
from django.urls import path, include

from .views import *

urlpatterns = [
    path('record/', Record.as_view(), name='record')
]