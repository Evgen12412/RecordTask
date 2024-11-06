from django.db import models

from audio_converter.models import VoiceRecording

from app.models import MyUser


# Create your models here.
class Transcription(models.Model):
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    record = models.ForeignKey(VoiceRecording, related_name='transcriptions', on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(MyUser,  on_delete=models.CASCADE)

    def __str__(self):
        return f"Транскрипция {self.id}"