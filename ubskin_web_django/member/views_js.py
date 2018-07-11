import os

from django.http import JsonResponse
from django.shortcuts import render
from django import forms
from django.forms.models import model_to_dict

from ubskin_web_django.member import models as member_models
from ubskin_web_django.common import photo
from ubskin_web_django.common import decorators

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
        error_messages={'required': '手机号不可为空'}
    )

    class Meta:
        model = member_models.Member
        fields = ('member_name', 'telephone', 'is_admin', 'is_staff')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("两次密码不一致")
        return password2


    def clean_telephone(self):
        telephone = self.cleaned_data.get("telephone")
        if telephone:
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

@decorators.js_authenticated
def create_member(request):
    return_value = {
        'status':'error',
        'message':'',
    }
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if not form.is_valid():
            return_value['message'] = list(form.errors.values())[0]
            return JsonResponse(return_value)
        form.save()
        return_value['status'] = 'success'
        return JsonResponse(return_value)

@decorators.js_authenticated
def delete_member(request):
    return_value = {
        'status':'error',
        'message':'',
    }
    if request.method == "POST":
        id_list = request.POST.getlist('member_id_list[]')
        member_models.Member.delete_members_by_id_list(id_list)
        return_value['status'] = 'success'
        return JsonResponse(return_value)


@decorators.js_authenticated
def editor_member(request):
    return_value = {
        'status':'error',
        'message':'',
    }
    update_field = ['member_name', 'telephone', 'is_admin', 'is_staff']
    member_id = request.GET.get('member_id')
    member_obj = member_models.Member.get_member_by_id(member_id)
    if request.method == 'GET':
        form_data = model_to_dict(member_obj)
        return_value['status'] = 'success'
        return_value['data'] = form_data
        return JsonResponse(return_value)
    else:
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        if password1 and password2:
            if password1 != password2:
                return_value['message'] = ['两次密码不一致']
                return JsonResponse(return_value)
            member_obj.set_password(password2)
        telephone = request.POST.get('telephone')
        if telephone:
            if member_models.Member.has_member_telephone(
                telephone, request.POST.get('member_id')):
                return_value['message'] = ['该手机号已经存在']
                return JsonResponse(return_value)
        clear_data = {
            key:request.POST.get(key) for key in update_field
        }
        clear_data['is_admin'] = True if clear_data['is_admin'] == 'true' else False
        clear_data['is_staff'] = True if clear_data['is_staff'] == 'true' else False
        member_models.Member.update_member_by_id(member_id, clear_data)
        return_value['status'] = 'success'
        return JsonResponse(return_value)


def jm_recv_addr_info(request):
    data_id = request.GET.get('data_id')
    data_list = member_models.RecvAddr.get_recv_addr_by_member_id(data_id)
    return render(
        request,
        'member/a_jm_recv_addr_info.html',
        {'data_list': data_list}
    )