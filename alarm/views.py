import os

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
# Create your views here.
from rest_framework.views import APIView
from audio_converter.models import VoiceRecording


from django.http import JsonResponse, FileResponse

import os
import logging

logger = logging.getLogger(__name__)

import os
import logging

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from django.http import JsonResponse, FileResponse

from audio_converter.models import VoiceRecording

logger = logging.getLogger(__name__)

@method_decorator(csrf_exempt, name='dispatch')
class TaskStatusView(APIView):
    def post(self, request):
        task_status = request.data.get('task')
        task_id = request.data.get('task_id')

        logger.debug(f"Received task status: {task_status}, task_id: {task_id}")

        if task_status == 'run':
            try:
                recording = VoiceRecording.objects.get(id=task_id)
                logger.debug(f"Found recording: {recording}")

                if recording.user != request.user:
                    logger.warning(f"Permission denied for user: {request.user}")
                    return JsonResponse({'status': 'error', 'message': 'Permission denied'}, status=403)

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
            logger.debug("Processing 'send' task status")
            pass

        return JsonResponse({'status': 'success', 'task_status': task_status, 'task_id': task_id})



