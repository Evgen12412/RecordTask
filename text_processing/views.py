import datetime
import logging
import os
from django.utils import timezone

import speech_recognition as sr
from django.http import JsonResponse
from pydub import AudioSegment
from rest_framework.views import APIView
import re

from audio_converter.models import VoiceRecording
from text_processing.models import Transcription

logger = logging.getLogger(__name__)


# Путь к файлу в корне проекта
ROOT_AUDIO_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'temp_audio.wav')


class Transcribe(APIView):
    def get(self, request, user_id):
        try:
            # Проверяем, существует ли файл в корне проекта
            if not os.path.exists(ROOT_AUDIO_FILE_PATH):
                logger.error(f"Audio file {ROOT_AUDIO_FILE_PATH} does not exist")
                return JsonResponse({'error': 'Audio file does not exist'}, status=404)

            # Преобразуем аудиофайл в формат mp3
            wav_file_path = self.converter(ROOT_AUDIO_FILE_PATH)

            # Инициализация распознавателя
            recognizer = sr.Recognizer()

            # Открытие аудиофайла с помощью AudioFile
            with sr.AudioFile(wav_file_path) as source:
                # Настройка на шум окружающей среды
                recognizer.adjust_for_ambient_noise(source)
                # Запись аудио
                audio = recognizer.record(source)

            # Распознавание речи с использованием Google Web Speech API
            transcript = recognizer.recognize_google(audio, language='ru-RU')

            # Извлекаем число из транскрибированного текста
            data_transcript = self.extract_number_from_string(transcript)

            # Если число найдено, используем его для создания времени
            if isinstance(data_transcript, tuple):
                hours, minutes = data_transcript
                completed_at = timezone.now().replace(hour=hours, minute=minutes, second=0, microsecond=0)
            else:
                # Если время не найдено, используем текущее время
                completed_at = timezone.now()

            voice_recording = VoiceRecording.objects.get(id=user_id)

            transcript_instance = Transcription.objects.create(
                text=transcript,
                completed_at=completed_at,
                user=request.user,
                record=voice_recording,
            )
            logger.info(f"Audio recording transcribed: {transcript_instance}")

            # Удаляем временный файл WAV
            os.remove(wav_file_path)

            # Сериализуем объект Transcription в JSON
            response_data = {
                'status': 'success',
                'transcript': transcript_instance.text,
                'completed_at': completed_at.strftime('%Y-%m-%d %H:%M:%S')
            }
            response = JsonResponse(response_data, json_dumps_params={'ensure_ascii': False})
            response["Content-Type"] = "application/json; charset=utf-8"
            return response
        except sr.UnknownValueError:
            logger.error("Google Web Speech API could not understand audio")
            return JsonResponse({'error': 'Google Web Speech API could not understand audio'}, status=500)
        except sr.RequestError as e:
            logger.error(f"Could not request results from Google Web Speech API; {e}")
            return JsonResponse({'error': f'Could not request results from Google Web Speech API; {e}'}, status=500)
        except Exception as e:
            logger.error(f"Failed to transcribe audio file: {e}")
            return JsonResponse({'error': str(e)}, status=500)

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

    def extract_number_from_string(self, text):
        # Регулярное выражение для поиска чисел в строке
        match = re.search(r'(\d{1,2}):(\d{2})', text)
        if match:
            hours = int(match.group(1))
            minutes = int(match.group(2))
            return (hours, minutes)
        else:
            # Возвращаем текущее время в формате строки
            return datetime.datetime.now().strftime('%H:%M:%S')

# Контекстный менеджер для удаления файлов после выполнения операций
class FileCleanup:
    def __init__(self, *files):
        self.files = files

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for file in self.files:
            if os.path.exists(file):
                os.remove(file)
                logger.info(f"Deleted file: {file}")