from django.shortcuts import render

from ubskin_web_django.order import models as order_models
from ubskin_web_django.item import models as item_models

# Create your views here.

def my_render(request, templater_path, **kwargs):
    return render(request, templater_path, dict(**kwargs))

def order_manage(request):
    if request.method == 'GET':
        current_page = request.GET.get('page', 1)
        value = request.GET.get('serch_value', '')
        filter_args = None
        if value:
            filter_args = '&search_value={0}'.format(value)
            search_value = {"out_order_id" : value}
            data_list = order_models.get_data_list(
                order_models.Order, current_page, search_value
            )
            item_count = order_models.get_data_count(
                order_models.Order, search_value
            )
        else:
            data_list = order_models.get_data_list(
                order_models.Order, current_page
            )
            print(data_list)
            item_count = order_models.get_data_count(order_models.Order)
        if data_list:
            for i in data_list:
                item_qr_code_count = order_models.ItemQRCode. \
                    get_count_by_out_order_id(i['out_order_id'])
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
            serch_value = value,
        )

def item_qr_Code_manage(request):
    if request.method == 'GET':
        current_page = request.GET.get('page', 1)
        value = request.GET.get('serch_value', '')
        filter_args = None
        if value:
            filter_args = '&search_value={0}'.format(value)
            search_value = {"item_code" : value}
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
            item_name = item_models.Items.get_item_name_by_barcode(i.get('item_barcode'))
            i['item_name'] = item_name
        return my_render(
            request,
            'order/a_item_qr_code_manage.html',
            data_list = data_list,
            current_page = current_page,
            filter_args = filter_args,
            serch_value = value,
            data_count = data_count,
        )

def recv_manage(request):
    if request.method == 'GET':
        current_page = request.GET.get('page', 1)
        value = request.GET.get('serch_value', '')
        filter_args = None
        if value:
            filter_args = '&search_value={0}'.format(value)
            search_value = {"recv_addr" : value}
            data_list = order_models.get_data_list(
                order_models.Recv, current_page, search_value, '-is_watch'
            )
            data_count = order_models.get_data_count(
                order_models.Recv, search_value
            )
        else:
            data_list = order_models.get_data_list(
                order_models.Recv, current_page, order_by='-is_watch'
            )
            data_count = order_models.get_data_count(order_models.Recv)
        return my_render(
            request,
            'order/a_recv_manage.html',
            data_list = data_list,
            filter_args = filter_args,
            serch_value = value,
            data_count = data_count,
        )

def out_order(request):
    if request.method == 'GET':
        return my_render(
            request,
            'order/a_out_order.html',
        )