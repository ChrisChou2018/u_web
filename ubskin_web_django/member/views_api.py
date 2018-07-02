import os
import random
import json

from django.views.decorators.csrf import csrf_exempt
from django import forms
from django.http import JsonResponse
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth import logout

from ubskin_web_django.common import decorators
from ubskin_web_django.member import models as member_models
from ubskin_web_django.common import request_wx_openid


@csrf_exempt
def signin(request):
    return_value  = {
        'status': 'error',
        'message': '',
        'data': '',
    }
    telephone = request.POST.get('username')
    password = request.POST.get('password')
    member =  member_models.Member.get_member_by_telephone(telephone)
    has_login = member.check_password(password)
    if has_login:
        login(request, member)
        return_value['status'] = 'success'
        return_value['data'] = {
            'sessionid': request.session.session_key,
            'member_name': member.member_name,
            'member_id': member.member_id,
        }
        return JsonResponse(return_value)
    else:
        return_value['message'] = '账号或者密码错误'
        return JsonResponse(return_value)

@decorators.api_authenticated
@csrf_exempt
def signin_out(request):
    return_value  = {
        'status': 'error',
        'message': '',
        'data': '',
    }
    logout(request)
    return_value['status'] = 'success'
    return JsonResponse(return_value)


class UserCreationFormWX(forms.ModelForm):
    

    class Meta:
        model = member_models.Member
        fields = ('member_name', 'wx_openid', 'avatar', 'is_staff')

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserCreationFormWX, self).save(commit=False)
        if commit:
            user.save()
        return user

def wx_regist_member(return_value, openid, name, avatar, session_key=None):
    user_data = {'wx_openid': openid, 'member_name': name, 'avatar': avatar, 'is_staff': False}
    if session_key is not None:
        user_data.update({'sessions': session_key})
    form  = UserCreationFormWX(user_data)
    if form.is_valid():
        member = form.save()
        return_value['status'] = 'success'
        return_value['data'] = [{'is_staff': member.is_staff, 'openid': openid},]
        return JsonResponse(return_value)
    else:
        return_value['message'] = "携带参数错误或缺少参数"
        return JsonResponse(return_value)


@csrf_exempt
def wx_signin(request):
    return_value  = {
        'status': 'error',
        'message': '',
        'data': '',
    }
    if request.method == 'POST':
        data = json.loads(request.body)
        name = data.get('name')
        avatar = data.get('avatar')
        appid = data.get('appid')
        js_code = data.get('js_code')
        secret = data.get('secret')
        rep =  request_wx_openid.request_user_session_key(
            appid, js_code, secret
        )
        rep_dict = json.loads(rep)
        openid = rep_dict.get('openid')
        session_key = rep_dict.get('session_key') 
        if openid is not None:
            member = member_models.Member.get_member_by_wx_openid(openid)
            if member:
                member.member_name = name
                member.avatar = avatar
                member.save()
                return_value['status'] = 'success'
                return_value['data'] = [{'is_staff': member.is_staff, 'openid': member.wx_openid},]
                return JsonResponse(return_value)
            else:
                return wx_regist_member(return_value, openid, name, avatar, session_key)
        else:
            return_value['message'] = '服务端微信验证接口出错'
            return JsonResponse(return_value)

class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(
        error_messages={'required': '不能为空'}
    )
    password2 = forms.CharField(
        error_messages={'required': '密码不能为空'}
    )
    member_name = forms.CharField(
        error_messages={'required': '用户名不能为空'}
    )
    telephone = forms.CharField(
        error_messages={'required': '手机号不能为空'}
    )

    class Meta:
        model = member_models.Member
        fields = ('member_name', 'telephone',)

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("两次密码不一致")
        return password2

    def clean_telephone(self):
        telephone = self.cleaned_data.get("telephone")
        member = member_models.Member.get_member_by_telephone(telephone)
        if member:
            raise forms.ValidationError("手机号已经被注册")
        return telephone

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

@csrf_exempt
def register(request):
    return_value = {
        'status': 'error',
        'message': '',
    }
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if not form.is_valid():
            return_value['message'] = list(form.errors.values())[0]
            return JsonResponse(return_value)
        form.save()
        return_value['status'] = 'success'
        return JsonResponse(return_value)

@csrf_exempt
def change_password(request):
    pass