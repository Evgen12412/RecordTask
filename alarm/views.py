import os
import logging

import telebot
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from django.http import JsonResponse, FileResponse

from audio_converter.models import VoiceRecording

from text_processing.models import Transcription

logger = logging.getLogger(__name__)

@method_decorator(csrf_exempt, name='dispatch')
class TaskStatusView(APIView):
    def post(self, request):
        task_status = request.data.get('task')
        task_id = request.data.get('task_id')

        logger.debug(f"Получен статус задачи: {task_status}, task_id: {task_id}")

        if task_status == 'run':
            try:
                recording = VoiceRecording.objects.get(id=task_id)
                logger.debug(f"Найдена запись: {recording}")

                if recording.user != request.user:
                    logger.warning(f"Разрешение отклонено для пользователя: {request.user}")
                    return JsonResponse({'status': 'error', 'message': 'Доступ запрещен'}, status=403)

                audio_file_path = recording.audio_file.path
                logger.debug(f"Audio file path: {audio_file_path}")

                if not os.path.exists(audio_file_path):
                    logger.error(f"Audio file not found: {audio_file_path}")
                    return JsonResponse({'status': 'error', 'message': 'Audio file not found'}, status=404)

                return FileResponse(open(audio_file_path, 'rb'), content_type='audio/mp3')

            except VoiceRecording.DoesNotExist:
                logger.error(f"Recording not found for task_id: {task_id}")
                return JsonResponse({'status': 'error', 'message': 'Recording not found'}, status=404)
            except Exception as e:
                logger.error(f"Error processing task status: {e}")
                return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

        elif task_status == 'stop':
            logger.debug("Processing 'stop' task status")
            pass

        elif task_status == 'send':
            task = get_object_or_404(Transcription, id=task_id)
            self.send_message(task.text)
            logger.debug("Processing 'send' task status")


        return JsonResponse({'status': 'success', 'task_status': task_status, 'task_id': task_id})


    def send_message(self, message):
        import threading
        from decouple import config


        api = config('TELEGRAM_API_TOKEN')
        chat_id = config('TELEGRAM_CHAT_ID')
        bot = telebot.TeleBot(api)

        def send_telegram_message():
            try:
                bot.send_message(chat_id=chat_id, text=message)
                logger.debug(f"Message sent: {message}")
            except Exception as e:
                logger.error(f"Error sending message: {e}")

        """
            Запуск отправки сообщения в отдельном потоке
            
        """
        threading.Thread(target=send_telegram_message).start()
