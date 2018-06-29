import functools

from django.http import JsonResponse
from django.contrib.sessions.models import Session

def api_authenticated(method):
    @functools.wraps(method)
    def wrapper(request, *args, **kwargs):
        return_data = dict()
        if not request.user.get_username():
            return_data["message"] = "你没有登陆"
            return_data["status"] = "error"
            return JsonResponse(return_data)
        return method(request, *args, **kwargs)
    return wrapper