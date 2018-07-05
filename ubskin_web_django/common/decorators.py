import functools
import json

from django.http import JsonResponse
from django.contrib.sessions.models import Session

from ubskin_web_django.member import models as member_model

def js_authenticated(fuc):
    @functools.wraps(fuc)
    def wrapper(request, *args, **kwargs):
        return_data = dict()
        if str(request.user) == "AnonymousUser":
            return_data["message"] = "你没有登陆"
            return_data["status"] = "error"
            return JsonResponse(return_data)
        return fuc(request, *args, **kwargs)
    return wrapper


def wx_api_authenticated(fuc):
    @functools.wraps(fuc)
    def wrapper(request, *args, **kwargs):
        openid = request.COOKIES.get('openid')
        if openid is not None:
            member = member_model.Member.get_member_by_wx_openid(openid)
            if not member:
                return JsonResponse({'status': 'error', 'message': '未登陆无法操作'})
        else:
            return JsonResponse({'status': 'error', 'message': '未登陆无法操作'})
        return fuc(request, *args, **kwargs)
    return wrapper