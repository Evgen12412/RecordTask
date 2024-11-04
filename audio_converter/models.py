from django.db import models

from app.models import MyUser


# Create your models here.
class VoiceRecording(models.Model):
    audio_file = models.FileField(upload_to='voice_recordings/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(MyUser, related_name='recordings', on_delete=models.CASCADE)

    def __str__(self):
        return f"Recording {self.id}"