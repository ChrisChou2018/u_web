import random
import string
import os

from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.conf import settings

from ubskin_web_django.order import models as order_models
from ubskin_web_django.item import models as item_models
from ubskin_web_django.common import lib_data


# Create your views here.

def my_render(request, templater_path, **kwargs):
    return render(request, templater_path, dict(**kwargs))

@login_required(login_url='/myadmin/signin/')
def order_manage(request):
    if request.method == 'GET':
        current_page = request.GET.get('page', 1)
        value = request.GET.get('search_value', '')
        filter_args = None
        if value:
            filter_args = '&search_value={0}'.format(value)
            search_value = {"stock_batch_id__icontains" : value}
            data_list = order_models.get_data_list(
                order_models.StockBatch, current_page, search_value
            )
            item_count = order_models.get_data_count(
                order_models.StockBatch, search_value
            )
        else:
            data_list = order_models.get_data_list(
                order_models.StockBatch, current_page
            )
            item_count = order_models.get_data_count(order_models.StockBatch)
        if data_list:
            for i in data_list:
                item_qr_code_count = order_models. \
                    StockBatchCount.get_item_count_by_stock_batch_id(i['stock_batch_id'])
                i['code_count'] = item_qr_code_count
        for i in data_list:
            recv_addr = order_models.Recv. \
                get_recv_addr_by_recv_code(i['recv_code'])
            i['recv_addr'] = recv_addr
        return my_render(
            request,
            'order/a_order_manage.html',
            data_list = data_list,
            current_page = current_page,
            filter_args = filter_args,
            data_count = item_count,
            search_value = value,
        )

@login_required(login_url='/myadmin/signin/')
def item_qr_Code_manage(request):
    if request.method == 'GET':
        current_page = request.GET.get('page', 1)
        value = request.GET.get('search_value', '')
        filter_args = None
        if value:
            id_list =  order_models.StockBatchCount.get_obj_by_stock_batch_id(value)
            filter_args = '&search_value={0}'.format(value)
            search_value = {"stock_batch_count_id__in" : id_list}
            data_list = order_models.get_data_list(
                order_models.ItemQRCode, current_page, search_value
            )
            data_count = order_models.get_data_count(
                order_models.ItemQRCode, search_value
            )
        else:
            data_list = order_models.get_data_list(
                order_models.ItemQRCode, current_page
            )
            data_count = order_models.get_data_count(order_models.ItemQRCode)
        for i in data_list:
            obj = order_models.get_model_obj_by_pk(
                order_models.StockBatchCount,
                i.get('stock_batch_count_id')
            )
            if obj:
                item_name = item_models.Items.get_item_name_by_barcode(obj.item_barcode)
                i['item_name'] = item_name
                i['item_barcode'] = obj.item_barcode
                i['stock_batch_id'] = obj.stock_batch_id
        return my_render(
            request,
            'order/a_item_qr_code_manage.html',
            data_list = data_list,
            current_page = current_page,
            filter_args = filter_args,
            search_value = value,
            data_count = data_count,
        )

@login_required(login_url='/myadmin/signin/')
def recv_manage(request):
    if request.method == 'GET':
        current_page = request.GET.get('page', 1)
        value = request.GET.get('search_value', '')
        filter_args = None
        if value:
            filter_args = '&search_value={0}'.format(value)
            search_value = {"recv_addr__icontains" : value}
            data_list = order_models.get_data_list(
                order_models.Recv, current_page, search_value,
            )
            data_count = order_models.get_data_count(
                order_models.Recv, search_value
            )
        else:
            data_list = order_models.get_data_list(
                order_models.Recv, current_page,
            )
            data_count = order_models.get_data_count(order_models.Recv)
        return my_render(
            request,
            'order/a_recv_manage.html',
            data_list = data_list,
            filter_args = filter_args,
            search_value = value,
            data_count = data_count,
            current_page = current_page
        )

@login_required(login_url='/myadmin/signin/')
def stock_batch(request):
    if request.method == 'GET':
        return my_render(
            request,
            'order/a_stock_batch.html',
        )

@login_required(login_url='/myadmin/signin/')
def batch_qr_code_manage(request):
    if request.method == 'GET':
        GET = request.GET.get
        filter_args_dict = {
            
        }
        current_page = GET('page', 1)
        filter_args = ''
        search_value = dict()
        for i in filter_args_dict:
            value = GET(i)
            if value:
                search_value.update({filter_args_dict[i]: value})
                filter_args += "&{}={}".format(i, value)
        else:
            if not filter_args:
                filter_args = None
        if search_value:
            data_list = order_models.get_data_list(
                order_models.BatchQrCode,
                current_page,
                search_value
            )
            data_count = order_models.get_data_count(
                order_models.BatchQrCode,
                search_value
            )
        else:
            data_list = order_models.get_data_list(
                order_models.BatchQrCode,
                current_page,
            )
            data_count = order_models.get_data_count(
                order_models.BatchQrCode,
            )
        return my_render(
            request,
            'order/a_batch_qr_code_manage.html',
            table_head = order_models.BatchQrCode.get_style_table_head(),
            current_page = current_page,
            filter_args = filter_args,
            data_list = data_list,
            data_count = data_count,
            from_data = request.GET,
        )

@login_required(login_url='/myadmin/signin/')
def create_batch_qr_code(request):
    data_id = request.GET.get('data_id')
    model_obj = None
    if data_id:
        model_obj = order_models.get_model_obj_by_pk(
            order_models.BatchQrCode,
            data_id,
        )
    recv_choices = order_models.Recv.get_recv_all_by_select()
    if request.method == 'GET':
        return my_render(
            request,
            'order/a_create_batch_qr_code.html',
            form_data = model_obj,
            recv_choices = recv_choices,
        )
    else:
        code_count = request.POST.get('code_count')
        try:
            code_count = int(code_count)
        except:
            code_count = 0
        message = request.POST.get('message')
        recv_code = request.POST.get('recv_code')
        if not model_obj:
            form_errors = dict()
            if not code_count:
                form_errors['code_count'] = '请填写生成二维码数量（非0）'
            if form_errors:
                return my_render(
                    request,
                    'order/a_create_batch_qr_code.html',
                    form_data = request.POST,
                    recv_choices = recv_choices,
                    form_errors = form_errors,
                )
            model_obj = order_models.create_model_data(
                order_models.BatchQrCode,
                {'code_count': code_count, 'message': message, 'recv_code': recv_code,
                'create_member': request.user.member_id}
            )
            while code_count > 0:
                qr_code = 'U'+ ''.join(
                    random.choice(string.ascii_lowercase + string.digits) \
                    for i in range(8)
                )
                if order_models.ItemQRCode.check_has_item_qr_code(qr_code):
                    continue
                else:
                    order_models.create_model_data(
                        order_models.ItemQRCode,
                        {'batch_qr_code_id': model_obj.batch_qr_code_id, 'qr_code': qr_code}
                    )
                    code_count -= 1
            return redirect(reverse('batch_qr_code_manage'))

def download_qr_code_file(request, data_id):
    data_list = order_models.ItemQRCode.get_data_list_by_batch_qr_code_id(data_id)
    media = settings.MEDIA_ROOT
    server_media = settings.MEDIA_URL
    temp_path = os.path.join(media, 'temp')
    server_media_temp_path = os.path.join(server_media, 'temp')
    if not os.path.exists(temp_path):
        os.makedirs(temp_path)
    temp_file_path = os.path.join(temp_path, 'temp''')
    server_media_temp_file_path = os.path.join(server_media_temp_path, 'temp')
    with open(temp_file_path, 'w') as w:
        for i in data_list:
            w.write(str(i[0]) + '\n')
    print(server_media_temp_file_path)
    return redirect(server_media_temp_file_path)
    
    

def create_recv(request):
    recv_data = lib_data.recv_code_dict1
    order_models.Recv.objects.all().delete()
    for k, v in recv_data.items():
        order_models.create_model_data(
            order_models.Recv,
            {'recv_code': k, 'recv_addr': v},
        )
    return HttpResponseRedirect('/myadmin/recv_manage/')
