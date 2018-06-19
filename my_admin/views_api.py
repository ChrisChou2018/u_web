import os
import random

from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django import forms
from django.http import JsonResponse
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.sessions.models import Session

from my_admin import item_models
from ubskin_web_django.common import photo
from ubskin_web_django.common import decorators
from my_admin import member_models

@csrf_exempt
def signin(request):
    return_value  = {
        'status': 'error',
        'message': '',
        'data': '',
    }
    telephone = request.POST.get('username')
    password = request.POST.get('password')
    user = authenticate(telephone=telephone, password=password)
    if user:
        login(request, user)
        return_value['status'] = 'success'
        return_value['data'] = {
            'sessionid': request.session.session_key,
            'member_name': user.member_name,
            'member_id': user.member_id,
        }
        return JsonResponse(return_value)
    else:
        return_value['message'] = '账号或者密码错误'
        return JsonResponse(return_value)

@decorators.api_authenticated
@csrf_exempt
def signin_out(request):
    logout(request)
    return JsonResponse({'message':'登出成功'})
    

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

    def clean_member_name(self):
        member_name = self.cleaned_data.get("member_name")
        member = member_models.Member.get_member_by_member_name(member_name)
        if member:
            raise forms.ValidationError("用户名已经存在")
        return member_name

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

@decorators.api_authenticated
def get_item_info(request):
    return_value  = {
        'status': 'error',
        'message': '',
        'data': '',
    }
    if request.method == 'GET':
        current_page = request.GET.get('page', 1)
        items = item_models.Items.get_items_list_for_api(current_page)
        return_value['status'] = 'success'
        return_value['data'] = items
        return JsonResponse(return_value)

@decorators.api_authenticated
def api_get_categories(request):
    return_value  = {
        'status': 'error',
        'message': '',
        'data': '',
    }
    if request.method == 'GET':
        data_list = item_models.Categories.get_categoreis_for_api()
        return_value['status'] = 'success'
        return_value['data'] = data_list
        return JsonResponse(return_value)

@decorators.api_authenticated
def filter_items(request):
    return_value  = {
        'status': 'error',
        'message': '',
        'data': '',
    }
    if request.method == 'GET':
        categorie_id = request.GET.get('categorie_id')
        current_page = request.GET.get('page', 1)
        datas = item_models.Items. \
            get_items_by_categorie_id(categorie_id, current_page)
        return_value['status'] = 'success'
        return_value['data'] = datas
        return JsonResponse(return_value)

@decorators.api_authenticated
def get_item_comment(request):
    return_value  = {
        'status': 'error',
        'message': '',
        'data': '',
    }
    if request.method == 'GET':
        item_id = request.GET.get('item_id', 1)
        current_page = request.GET.get('page', 1)
        item_comment_data = item_models.ItemComments. \
            get_item_comment_by_item_id(item_id, current_page)
        return_value['status'] = 'success'
        return_value['data'] = item_comment_data
        return JsonResponse(return_value)


class CreateCommentForm(forms.ModelForm):
    class Meta:
        model = item_models.ItemComments
        fields = ('member_id', 'item_id', 'comment_content',)

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(CreateCommentForm, self).save(commit=False)
        if commit:
            user.save()
        return user


@decorators.api_authenticated
@csrf_exempt
def create_item_comment(request):
    return_value = {
        'status': 'error',
        'message': '',
        'data': '',
    }
    if request.method == 'POST':
        form = CreateCommentForm(request.POST)
        if not form.is_valid():
            return_value['message'] = list(form.errors.values())[0]
            return JsonResponse(return_value)
        obj = form.save()
        comment_image_list = []
        files = request.FILES
        if files:
            for i in files:
                file_obj = files[i]
                server_file_path = '/media/photos'
                file_dir = os.path.join(
                    settings.MEDIA_ROOT,
                    'photos'
                )
                if not os.path.exists(file_dir):
                    os.makedirs(file_dir)
                data = photo.save_upload_photo(
                    file_obj,
                    file_dir,
                    server_file_path,
                    'comment'
                )
                if data:
                    data['comment_id'] = obj.comment_id
                    comment_image_list.append(data)
            else:
                item_models.CommentImages. \
                create_many_comment_image(comment_image_list)
        return_value['status'] = 'success'
        return JsonResponse(return_value)