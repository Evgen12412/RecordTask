from django.urls import path, include

from .views import *

urlpatterns = [
    path('task-status/', TaskStatusView.as_view(), name='task_status'),
]