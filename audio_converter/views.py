import os
from django.core.files.base import ContentFile
from django.shortcuts import render
import speech_recognition as sr
from pydub import AudioSegment
from django.http import JsonResponse
from django.contrib.auth import login, logout, authenticate
from rest_framework.views import APIView

from .models import  VoiceRecording
from django.shortcuts import render, redirect, get_object_or_404
import logging
import json
import requests


logger = logging.getLogger(__name__)


# Путь к файлу в корне проекта
ROOT_AUDIO_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'temp_audio.wav')

class Record(APIView):

    def post(self, request):
        if request.method == 'POST' and request.FILES.get('audio_file'):
            audio_file = request.FILES['audio_file']

            # Создаем временный файл для сохранения аудио в корне проекта
            with open(ROOT_AUDIO_FILE_PATH, 'wb+') as destination:
                for chunk in audio_file.chunks():
                    destination.write(chunk)

            try:
                # Получаем текущего пользователя
                user = request.user
                audio_file_mp3 = self.converter(ROOT_AUDIO_FILE_PATH)

                # Читаем файл с использованием open
                with open(audio_file_mp3, 'rb') as audio_file_mp3_content:
                    # Создаем новую запись в базе данных с аудиофайлом mp3
                    recording = VoiceRecording.objects.create(
                        audio_file=ContentFile(audio_file_mp3_content.read(), name='temp_audio.wav'), user=user)

                return JsonResponse({'status': 'success', 'recording_id': recording.id})
            except Exception as e:
                logger.error(f"Error processing audio file: {e}")
                return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

        return JsonResponse({'status': 'error', 'message': 'No audio file provided'}, status=400)




    def converter(self,  audio_file_path):
        try:
            # Проверяем, существует ли файл
            if not os.path.exists(audio_file_path):
                logger.error(f"Audio file {audio_file_path} does not exist")
                raise FileNotFoundError(f"Audio file {audio_file_path} does not exist")

            # Загружаем аудиофайл с помощью pydub
            audio = AudioSegment.from_file(audio_file_path)
            # Создаем временный файл для сохранения в формате WAV
            temp_wav_path = os.path.splitext(audio_file_path)[0] + "_temp.wav"
            # Экспортируем аудиофайл в формате WAV
            audio.export(temp_wav_path, format="wav")
            return temp_wav_path
        except Exception as e:
            logger.error(f"Failed to convert audio file {audio_file_path} to WAV: {e}")
            raise


