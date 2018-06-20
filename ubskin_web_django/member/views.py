import os

from django.shortcuts import render
from django.http import HttpResponseRedirect as redirect
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django import forms

from ubskin_web_django.member import models as member_models
from ubskin_web_django.common import photo


def my_render(request, templater_path, **kwargs):
    return render(request, templater_path, dict(**kwargs))

def member_signin(request):
    if request.method == "GET":
        return my_render(
            request,
            'member/a_signin.html',
        )
    else:
        telephone = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(telephone=telephone, password=password)
        if user and user.is_admin:
            login(request, user)
            return redirect('/index/')
        else:
            return my_render(
                request,
                'member/a_signin.html',
                form_error = '用户名或者密码错误',
                form_data = request.POST
            )

def member_signout(request):
    logout(request)
    return redirect('/signin/')

@login_required(login_url='/signin/')
def index(request):
    if request.method == "GET":
        return render(
            request,
            'a_index.html'
        )


class UserChangeForm(forms.ModelForm):

    password2 = forms.CharField(error_messages={'required': '新密码不能为空'})

    class Meta:
        model = member_models.Member
        fields = set()

    def clean_password(self):
        password = self.cleaned_data["password2"]
        return password

    def update_pass(self):
        user = super(UserChangeForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password2"])
        user.save()


@login_required(login_url='/signin/')
def change_pass(request):
    if request.method == 'GET':
        return my_render(
            request,
            'member/a_change_password.html',
        )
    else:
        password = request.POST.get('password')
        telephone = request.user.telephone
        user = authenticate(telephone=telephone, password=password)
        if not user:
            return my_render(
                request,
                'member/a_change_password.html',
                form_error = '原密码错误',
                form_data = request.POST
            )
        form = UserChangeForm(request.POST)
        if not form.is_valid():
            return my_render(
                request,
                'member/a_change_password.html',
                form_error = form.errors.get('password2'),
                form_data = request.POST
            )
        form.update_pass()
        return redirect('/signin/')

def member_manage(request):
    if request.method == "GET":
        GET = request.GET.get
        current_page = GET('page', 1)
        value = GET('search_value', '')
        filter_args = None
        if value:
            filter_args = '&search_value={0}'.format(value)
            search_value = (
                Q(member_name = value) | \
                Q(telephone = value)
            )
            member_list = member_models.Member. \
                get_member_list(current_page, search_value)
            member_count = member_models.Member. \
                get_member_count(search_value)
        else:
            member_list = member_models.Member. \
            get_member_list(current_page)
            member_count = member_models.Member.get_member_count()
        uri = request.path
        table_head = member_models.Member.get_style_table_head()
        return my_render(
            request,
            'member/a_member_manage.html',
            current_page = current_page,
            member_list = member_list,
            member_count = member_count,
            uri = uri,
            filter_args = filter_args,
            table_head = table_head,
            search_value = value
        )