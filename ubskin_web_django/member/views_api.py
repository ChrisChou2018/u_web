import os
import random
import json
from json import JSONDecodeError
import string
import time

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
        rep_dict =  request_wx_openid.request_user_session_key(
            appid, js_code, secret
        )
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
            return_value['message'] = '微信接口验证出错,请重新登陆'
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

def check_is_staff(request, openid):
    return_value = {
        'status': 'error',
        'message': ''
    }
    if request.method == "GET":
        member = member_models.Member.get_member_by_wx_openid(openid)
        if member and member.is_staff:
            return_value['status'] = 'success'
            return_value['data'] = {'is_staff': True}
        else:
            return_value['status'] = 'success'
            return_value['data'] = {'is_staff': False}
        return JsonResponse(return_value)

@csrf_exempt
@decorators.wx_api_authenticated
def create_recv_addr(request):
    return_value = {
        'status': 'error',
        'message': '',
    }
    if request.method == 'POST':
        openid = request.COOKIES.get('openid')
        data = json.loads(request.body)
        address = data.get('address')
        area = data.get('area')
        area_code = data.get('area_code')
        username = data.get('username')
        telephone = data.get('telephone')
        member = member_models.Member.get_member_by_wx_openid(openid)
        member_models.create_model_data(
            member_models.RecvAddr,
            {'member_id': member.member_id,
            'address': address,
            'area': area,
            'area_code': area_code,
            'username': username,
            'telephone': telephone}
        )
        return_value['status'] = 'success'
        return JsonResponse(return_value)

@decorators.wx_api_authenticated

def get_recv_addr(request):
    return_value = {
        'status': 'error',
        'message': '',
    }
    if request.method == 'GET':
        openid = request.COOKIES.get('openid')
        member = member_models.Member.get_member_by_wx_openid(openid)
        data_list = member_models.RecvAddr. \
            get_recv_addr_by_member_id(member.member_id)
        return_value['status'] = 'success'
        return_value['data'] = data_list
        return JsonResponse(return_value)

@csrf_exempt
@decorators.wx_api_authenticated
def delete_recv_addr(request):
    return_value = {
        'status': 'error',
        'message': '',
    }
    if request.method == 'POST':
        data = request.body
        data = json.loads(data)
        recv_addr_id_list = data.get('recv_addr_id_list')
        for i in recv_addr_id_list:
            member_models.update_model_data_by_pk(
                member_models.RecvAddr,
                i,
                {'status': 'deleted'}
            )
        return_value['status'] = 'success'
        return JsonResponse(return_value)

@csrf_exempt
@decorators.wx_api_authenticated
def update_recv_addr(request):
    return_value = {
        'status': 'error',
        'message': '',
    }
    if request.method == 'GET':
        recv_addr_id = int(request.GET.get('recv_addr_id'))
        recv_addr = member_models.get_model_dict_by_pk(
            member_models.RecvAddr,
            recv_addr_id
        )
        if recv_addr:
            return_value['status'] = 'success'
            return_value['data'] = recv_addr
            return JsonResponse(return_value)
        else:
            return_value['message'] = "数据出错"
            return JsonResponse(return_value)
    else:
        openid = request.COOKIES.get('openid')
        member = member_models.Member.get_member_by_wx_openid(openid)
        data = request.body
        data = json.loads(data)
        recv_addr_id = int(data.get('recv_addr_id'))
        update_data = data.get('update_data')
        if 'is_default' in update_data:
            is_default = update_data.pop('is_default')
            member_models.RecvAddr.set_is_default(
                member.member_id,
                recv_addr_id,
                is_default
            )
            
        member_models.update_model_data_by_pk(
            member_models.RecvAddr,
            recv_addr_id,
            update_data
        )
        return_value['status'] = 'success'
        return JsonResponse(return_value)

@decorators.wx_api_authenticated
def get_user_order(request):
    return_value = {
        'status': 'error',
        'message': ''
    }
    if request.method == 'GET':
        openid = request.COOKIES.get('openid')
        member = member_models.Member.get_member_by_wx_openid(openid)
        data_dict = member_models.UserOrder.get_user_order_by_member_id(member.member_id)
        return_value['status'] = 'success'
        return_value['data'] = data_dict
        return JsonResponse(return_value)

@decorators.wx_api_authenticated
def get_user_order_info(request, order_num):
    return_value = {
        'status': 'error',
        'message': ''
    }
    if request.method == 'GET':
        user_order = member_models.UserOrder.get_user_order_by_order_num(order_num)
        return_value['status'] = 'success'
        return_value['data'] = user_order
        return JsonResponse(return_value)

@csrf_exempt
@decorators.wx_api_authenticated
def create_user_order(request):
    return_value = {
        'status': 'error',
        'message': ''
    }
    if request.method == 'POST':
        openid = request.COOKIES.get('openid')
        member = member_models.Member.get_member_by_wx_openid(openid)
        data = request.body
        data = json.loads(data)
        recv_addr_id = data.get('recv_addr_id')
        order_info = data.get('order_info')
        order_num = None
        print(data)
        while True:
            order_num = ''.join(
                random.choice(string.digits) \
                for i in range(19)
            )
            if member_models.UserOrder.has_order_num(order_num):
                pass
            else:
                break
        for i in order_info:
            i.update({
                'create_time': int(time.time()),
                'member_id': member.member_id,
                'recv_addr_id': recv_addr_id,
                'order_num': order_num
            })
            member_models.create_model_data(
                member_models.UserOrder,
                i
            )
        return_value['status'] = 'success'
        return JsonResponse(return_value)
        

def success_recv(request):
    if request.method == 'POST':
        data = request.body
        data = json.loads(data)

