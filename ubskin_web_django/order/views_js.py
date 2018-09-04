import json
import time

from django import forms
from django.http import JsonResponse
from django.forms.models import model_to_dict
from django.shortcuts import render

from ubskin_web_django.order import models as order_models
from ubskin_web_django.item import models as item_models
from ubskin_web_django.common import lib_data

def my_render(request, templater_path, **kwargs):
    return render(request, templater_path, dict(**kwargs))


class RecvForm(forms.ModelForm):
    class Meta:
        model = order_models.Recv
        fields = ('recv_code', 'recv_addr',)
    

    def save(self, commit=True):
        # Save the provided password in hashed format
        recv = super(RecvForm, self).save(commit=False)
        if commit:
            recv.save()
        return recv
    
    def update(self, pk):
        model = self._meta.model
        data = self.cleaned_data
        order_models.update_models_by_pk(model, pk, data)

def create_recv(request):
    return_value = {
        'status': 'error',
        'message': '',
    }
    if request.method == 'POST':
        form = RecvForm(request.POST)
        if not form.is_valid():
            return_value['message'] = list(form.errors.values())[0]
            return JsonResponse(return_value)
        form.save()
        return_value['status'] = 'success'
        return JsonResponse(return_value)

def set_recv_watch(request):
    return_value = {
        'status': 'error',
        'message': '',
    }
    if request.method == 'POST':
        recv_id = request.POST.get('cid')
        recv_obj = order_models.get_model_obj_by_pk(order_models.Recv, recv_id)
        is_watch = True
        if recv_obj:
            is_watch = recv_obj.is_watch
        if is_watch:
            is_watch = False
        else:
            is_watch = True
        order_models.update_models_by_pk(order_models.Recv, recv_id, {'is_watch': is_watch})
        return_value['status'] = 'success'
        return JsonResponse(return_value)
        
def delete_recv(request):
    return_value = {
        'status': 'error',
        'message': '',
    }
    if request.method == 'POST':
        recv_id_list = request.POST.getlist('recv_id_list[]')
        order_models.delete_models_by_pk(order_models.Recv, recv_id_list)
        return_value['status'] = 'success'
        return JsonResponse(return_value)

def edit_recv(request):
    return_value = {
        'status': 'error',
        'message': '',
    }
    recv_id = request.GET.get('recv_id')
    if request.method == 'GET':
        recv_obj =  order_models.get_model_obj_by_pk(order_models.Recv, recv_id)
        form_data = model_to_dict(recv_obj)
        return_value['status'] = 'success'
        return_value['data'] = form_data
        return JsonResponse(return_value)
    
    else:
        form = RecvForm(request.POST)
        if not form.is_valid():
            return_value['message'] = list(form.errors.values())[0]
            return JsonResponse(return_value)
        form.update(recv_id)
        return_value['status'] = 'success'
        return JsonResponse(return_value)

def get_reve_addr(request):
    return_value = {
        'status': 'error',
        'message': '',
        'data': '',
    }
    if request.method == 'GET':
        recv_code = request.GET.get('recv_code')
        stock_batch_id = request.GET.get('stock_batch_id')
        if order_models.StockBatch.check_has_stock_batch_id(stock_batch_id):
            return_value['message'] = '该出库单号已经存在'
            return JsonResponse(return_value)
        recv_addr = order_models.Recv.get_recv_addr_by_recv_code(recv_code)
        if recv_addr:
            return_value['status'] = 'success'
            return_value['data'] = {'recv_addr': recv_addr}
            return JsonResponse(return_value)
        else:
            return_value['message'] = '没有找到相关地址'
            return JsonResponse(return_value)

def get_item_info_by_code(request):
    return_value = {
        'status': 'error',
        'message': '',
    }
    if request.method == 'GET':
        item_barcode = request.GET.get('item_barcode')
        recv_code = request.GET.get('recv_code')
        if not item_barcode:
            return_value['message'] = '无效的商品码'
            return JsonResponse(return_value)
        item_dict = item_models.Items.get_item_dict_by_item_barcode(item_barcode)
        brand_id = item_dict.get('brand_id')
        brand = None
        if brand_id:
            brand = item_models.get_model_obj_by_pk(item_models.Brands, brand_id)
        if item_dict is None:
            return_value['message'] = '没有找到相关的商品'
            return JsonResponse(return_value)
        recv = order_models.Recv.get_recv_obj_by_recv_code(recv_code)
        if recv:
            return_value['in_monitor'] = True if recv.is_watch else False
            if brand_id and brand:
                return_value['in_monitor'] = True if recv.is_watch and brand.is_watch else False
        item_dict.pop("item_id")
        return_value['status'] = 'success'
        return_value['data'] = item_dict
        return JsonResponse(return_value)

def create_stock_bach(request):
    return_value = {
        'status': 'error',
        'message': '',
    }
    if request.method == 'POST':
        stock_batch_id = request.POST.get('stock_batch_id')
        recv_code = request.POST.get('recv_code')
        item_codes_dict = json.loads(request.POST.get('item_codes_dict'))
        nums_dict = json.loads(request.POST.get('nums_dict'))
        create_user_id = request.user.member_id
        if not recv_code or not stock_batch_id or not (item_codes_dict or  nums_dict):
            return_value['message'] = "提交数据有误，请确认"
            return JsonResponse(return_value)
        order_models.create_model_data(
            order_models.StockBatch,
            {
                "stock_batch_id": stock_batch_id,
                "recv_code": recv_code,
                "create_user": create_user_id,
                "create_time": int(time.time())
            }
        )
        if item_codes_dict:
            for key, item in item_codes_dict.items():
                if not item:
                    continue
                for i in item:
                    if not (len(i) == 9 and i.startswith('U')):
                        return_value['message'] = '商品二维码格式错误'
                        return JsonResponse(return_value)
                stock_batch_count = order_models.create_model_data(
                    order_models.StockBatchCount,
                    {
                        'item_barcode': key,
                        'stock_batch_id': stock_batch_id,
                        'item_count': len(item),
                    }
                )
                for i in item:
                    qr_code_obj = order_models.ItemQRCode.get_qr_code_obj_by_qr_code(i)
                    qr_code_obj.stock_batch_count_id =  stock_batch_count.stock_batch_count_id
                    qr_code_obj.create_user = create_user_id
                    qr_code_obj.save()
                    # order_models.create_model_data(
                    #     order_models.ItemQRCode,
                    #     {
                    #         "qr_code": i,
                    #         "stock_batch_count_id": stock_batch_count.stock_batch_count_id,
                    #         "create_user": create_user_id
                    #     }
                    # )
        else:
            for key, item in nums_dict.items():
                if int(item) == 0:
                    continue 
                order_models.create_model_data(
                    order_models.StockBatchCount,
                    {
                        "item_barcode": key,
                        "stock_batch_id": stock_batch_id,
                        "item_count": int(item),
                    }
                )
        return_value['status'] = 'success'
        return JsonResponse(return_value)

def jm_stock_batch_info(request):
    data_id = request.GET.get('data_id')
    if data_id:
        code_data = order_models.ItemQRCode. \
            get_stock_batch_info_by_stock_batch_id(data_id)
        return my_render(
            request,
            'order/a_jm_stock_batch_info.html',
            code_data = code_data
        )
    else:
        return my_render(
            request,
            'order/a_empty.html',
        )

def check_has_item_qr_code(request):
    return_value = {
        'status': 'error',
        'message': '',
    }
    if request.method == 'GET':
        item_qr_code = request.GET.get('item_qr_code')
        has = order_models.ItemQRCode.check_has_item_qr_code(item_qr_code)
        if not has:
            return_value['message'] = '当前二维码无效'
            return JsonResponse(return_value)
        elif has.stock_batch_count_id:
            return_value['message'] = '当前二维码已被录入'
            return JsonResponse(return_value)
        else:
            return_value['status'] = 'success'
            return JsonResponse(return_value)

def delete_batch_qr_code(request):
    return_value = {
        'status': 'error',
        'message': '',
    }
    if request.method == 'POST':
        data_id_list = request.POST.getlist('data_id_list[]')
        for i in data_id_list:
            order_models.update_models_by_pk(
                order_models.BatchQrCode,
                i,
                {'status': 'deleted'}
            )
            order_models.ItemQRCode.delete_data_by_batch_qr_code_id(i)
        return_value['status'] = 'success'
        return JsonResponse(return_value)

def delete_stockbatch(request):
    return_value = {
        'status': 'error',
        'message': '',
    }
    if request.method == 'POST':
        data_id_list = request.POST.getlist('data_id_list[]')
        for i in data_id_list:
            order_models.StockBatch.delete_data_by_stock_batch_id(i)
            order_models.StockBatchCount.delete_sb_count_by_sb_id(i)
        return_value['status'] = 'success'
        return JsonResponse(return_value)