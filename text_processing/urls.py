from django.urls import path

from .views import *

urlpatterns = [
    path('transcribe/<int:user_id>/', Transcribe.as_view(), name='transcribe'),
]