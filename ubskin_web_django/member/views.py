import os
import time

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
        user_name = request.POST.get('username')
        member = member_models.Member.get_member_by_telephone(user_name)
        password = request.POST.get('password')
        user = authenticate(user_name=user_name, password=password)
        if user and user.is_admin:
            login(request, user)
            return redirect('/myadmin/index/')
        elif member:
            if member.check_password(password):
                login(request, member)
                return redirect('/myadmin/index/')
            else:
                return my_render(
                    request,
                    'member/a_signin.html',
                    form_error = '用户名或者密码错误',
                    form_data = request.POST
                )
        else:
            return my_render(
                request,
                'member/a_signin.html',
                form_error = '用户名或者密码错误',
                form_data = request.POST
            )

def member_signout(request):
    logout(request)
    return redirect('/myadmin/signin/')

@login_required(login_url='/myadmin/signin/')
def index(request):
    if request.method == "GET":
        return render(
            request,
            'a_index.html'
        )



@login_required(login_url='/myadmin/signin/')
def change_pass(request):
    if request.method == 'GET':
        return my_render(
            request,
            'member/a_change_password.html',
        )
    else:
        password = request.POST.get('password')
        pas = request.user.check_password(password)
        if not pas:
            return my_render(
                request,
                'member/a_change_password.html',
                form_error = '原密码错误',
                form_data = request.POST
            )
        request.user.set_password(request.POST.get('password2'))
        request.user.save()
        return redirect('/myadmin/signin/')

@login_required(login_url='/myadmin/signin/')
def member_manage(request):
    if request.method == "GET":
        GET = request.GET.get
        current_page = GET('page', 1)
        value = GET('search_value', '')
        filter_args = None
        if value:
            filter_args = '&search_value={0}'.format(value)
            search_value = (
                Q(member_name__icontains = value) | \
                Q(telephone__icontains = value)
            )
            member_list = member_models.get_data_list(
                member_models.Member,
                current_page,
                search_value,
                search_value_type='not_dict'
            )
            member_count = member_models.get_data_count(
                member_models.Member,
                search_value,
                search_value_type='not_dict',
            )
        else:
            member_list = member_models.get_data_list(
                member_models.Member,
                current_page
            )
            member_count = member_models.get_data_count(
                member_models.Member
            )
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


def recv_addr(request):
    if request.method == "GET":
        current_page = request.GET.get('page', 1)
        value = request.GET.get('search_value', '')
        filter_args = None
        if value:
            filter_args = '&search_value={0}'.format(value)
            search_value = {"member_id__icontains" : value}
            data_list = member_models.RecvAddr.get_recv_addr_data_list(
                current_page,
                search_value
            )
            data_count = member_models.RecvAddr. \
                get_recv_addr_count(search_value)
        else:
            data_list = member_models.RecvAddr. \
                get_recv_addr_data_list(current_page)
            data_count = member_models.RecvAddr.get_recv_addr_count()
        return my_render(
            request,
            'member/a_recv_addr_manage.html',
            current_page = current_page,
            filter_args = filter_args,
            data_list = data_list,
            data_count = data_count,
            search_value = value,
        )

@login_required(login_url='/myadmin/signin/')
def user_order_manage(request):
    # '07/18/2018', '07/18/2018
    if request.method == 'GET':
        GET = request.GET.get
        filter_args_dict = {
            'search_value': 'order_num__icontains',
            'datetime': 'create_time__range',
            'order_status': 'order_status',
        }
        current_page = GET('page', 1)
        filter_args = '&'
        search_value = dict()
        for i in filter_args_dict:
            value = GET(i)
            if value:
                if i == 'datetime':
                    start_time, end_time = value.split(' - ')
                    start_time = time.mktime(time.strptime(start_time, r'%m/%d/%Y'))
                    end_time = time.mktime(time.strptime(end_time, r'%m/%d/%Y'))
                    search_value.update({filter_args_dict[i]: (start_time, end_time)})
                else:
                    search_value.update({filter_args_dict[i]: value})
                filter_args += "{}={}".format(i, value)
        else:
            if len(filter_args) == 1:
                filter_args = None
        if search_value:
            data_list = member_models.UserOrder.get_user_order_list(
                current_page,
                search_value
            )
            data_count = member_models.UserOrder. \
                get_user_order_count(search_value)
        else:
            data_list = member_models.UserOrder. \
                get_user_order_list(current_page)
            data_count = member_models.UserOrder.get_user_order_count()
        order_status = member_models.UserOrder.status_choices
        for i in data_list:
            member = member_models.Member.get_member_by_id(i['member_id'])
            i['member_id'] = member.member_name if member else '无此用户'
        return my_render(
            request,
            'member/a_user_order_manage.html',
            order_status = order_status,
            current_page = current_page,
            filter_args = filter_args,
            data_list = data_list,
            data_count = data_count,
            from_data = request.GET,
        )

def out_order_manage(request):
    if request.method == 'GET':
        current_page = request.GET.get('page', 1)
        value = request.GET.get('search_value', '')
        filter_args = None
        if value:
            filter_args = '&search_value={0}'.format(value)
            search_value = {"cn_name__icontains": value}
            data_list = member_models.get_data_list(
                member_models.OutOrder,
                current_page,
                search_value
            )
            data_count = member_models.get_data_count(
                member_models.OutOrder,
                search_value
            )
        else:
            data_list = member_models.get_data_list(
                member_models.OutOrder,
                current_page,
            )
            data_count = member_models.get_data_count(
                member_models.OutOrder,
            )
        for i in data_list:
            for j in i:
                if  type(i[j]) is str and i[j].startswith('b'):
                    i[j] = eval(i[j]).decode()
        return my_render(
            request,
            'member/a_out_order_manage.html',
            search_value = value,
            current_page = current_page,
            filter_args = filter_args,
            data_list = data_list,
            data_count = data_count,
            default_table_head = member_models.OutOrder.default_table_head(),
        )