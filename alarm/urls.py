from django.urls import path, include

from .views import TaskStatusView

urlpatterns = [
    path('task-status/', TaskStatusView.as_view(), name='task_status'),
]