from django.http import JsonResponse
from django import forms
from django.forms.models import model_to_dict

from my_admin import member_models
from my_admin import member_models


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
        fields = ('member_name', 'telephone', 'is_admin')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("两次密码不一致")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


def create_member(request):
    return_value = {
        'status':'error',
        'msg':'',
    }
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if not form.is_valid():
            return_value['msg'] = list(form.errors.values())
            return JsonResponse(return_value)
        form.save()
        return_value['status'] = 'success'
        return JsonResponse(return_value)

def delete_member(request):
    return_value = {
        'status':'error',
        'msg':'',
    }
    if request.method == "POST":
        id_list = request.POST.getlist('member_id_list[]')
        member_models.Member.delete_members_by_id_list(id_list)
        return_value['status'] = 'success'
        return JsonResponse(return_value)


def editor_member(request):
    return_value = {
        'status':'error',
        'msg':'',
    }
    update_field = ['member_name', 'telephone', 'is_admin']
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
                return_value['msg'] = ['两次密码不一致']
                return JsonResponse(return_value)
            member_obj.set_password(password2)
        clear_data = {
            key:request.POST.get(key) for key in update_field 
            if request.POST.get(key)
        }
        clear_data['is_admin'] = True if clear_data['is_admin'] == 'true' else False
        member_models.Member.update_member_by_id(member_id, clear_data)
        return_value['status'] = 'success'
        return JsonResponse(return_value)
        