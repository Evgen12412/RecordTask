from django.urls import path

from .views import TaskStatusView

urlpatterns = [
    path('task-status/', TaskStatusView.as_view(), name='task_status'),
]