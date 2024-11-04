from django.contrib import admin

from .models import MyUser
from text_processing.models import Transcription

from audio_converter.models import VoiceRecording

# Register your models here.
admin.site.register(MyUser)
admin.site.register(Transcription)
admin.site.register(VoiceRecording)