from django.shortcuts import render

from django.middleware.csrf import get_token

from ks_audio.models import Audio, AudioWeek, AudioCourse, AudioArticle


def get_csrf_token(request):
    csrf_token = get_token(request)
    return JsonResponse({'csrfToken': csrf_token})

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def get_audio_url(request):
    if request.method == 'POST':
        http_x_csrf_token = request.META.get('HTTP_X_CSRFTOKEN')
        cookie_csrf_token = request.COOKIES.get('csrftoken', '')
        print(http_x_csrf_token)
        print(cookie_csrf_token)
        if http_x_csrf_token == cookie_csrf_token:
            audio_id = int(request.POST.get('audio_id'))
            audio_type = request.POST.get('audio_type')
            if audio_type == "CCDETAIL":
                try:
                    audio_file = Audio.objects.get(id=audio_id)
                    if not audio_file.is_lock:
                        audio_url = audio_file.url
                        return JsonResponse({'url': audio_url})
                    else:
                        return JsonResponse({'error': 'File is locked'}, status=403)
                except Audio.DoesNotExist:
                    return JsonResponse({'error': 'File not found'}, status=404)
            elif audio_type == "WEEK":
                try:
                    audio_file = AudioWeek.objects.get(id=audio_id)
                    if not audio_file.is_lock:
                        audio_url = audio_file.url
                        return JsonResponse({'url': audio_url})
                    else:
                        return JsonResponse({'error': 'File is locked'}, status=403)
                except AudioWeek.DoesNotExist:
                    return JsonResponse({'error': 'File not found'}, status=404)
            elif audio_type == "COURSE":
                try:
                    audio_file = AudioCourse.objects.get(id=audio_id)
                    if not audio_file.is_lock:
                        audio_url = audio_file.url
                        return JsonResponse({'url': audio_url})
                    else:
                        return JsonResponse({'error': 'File is locked'}, status=403)
                except AudioCourse.DoesNotExist:
                    return JsonResponse({'error': 'File not found'}, status=404)
            elif audio_type == "ARTICLE":
                try:
                    audio_file = AudioArticle.objects.get(id=audio_id)
                    if not audio_file.is_lock:
                        audio_url = audio_file.url
                        return JsonResponse({'url': audio_url})
                    else:
                        return JsonResponse({'error': 'File is locked'}, status=403)
                except AudioArticle.DoesNotExist:
                    return JsonResponse({'error': 'File not found'}, status=404)
            else:
                pass

        else:
            return JsonResponse({'error': 'Invalid CSRF Token'}, status=403)

