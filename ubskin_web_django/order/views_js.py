import json

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
    }
    if request.method == 'GET':
        recv_code = request.GET.get('recv_code')
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
        if item_dict is None:
            return_value['message'] = '没有找到相关的商品'
            return JsonResponse(return_value)
        if recv_code and recv_code in lib_data.monitor_recv_codes:
            return_value['in_monitor'] = True \
                if item_dict["brand_name"] in lib_data.monitor_brand_names else False
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
        item_codes_dict = request.POST.get('item_codes_dict')
        item_codes_dict = json.loads(item_codes_dict)
        order_models.create_model_data(
            order_models.StockBatch,
            {"stock_batch_id": stock_batch_id, "recv_code": recv_code}
        )
        for key, item in item_codes_dict.items():
            for i in item:
                order_models.create_model_data(
                    order_models.ItemQRCode,
                    {
                        "item_barcode": key,
                        "qr_code": i,
                        "stock_batch_id": stock_batch_id
                    }
                )
        return_value['status'] = 'success'
        return JsonResponse(return_value)

def jm_stock_batch_info(request):
    data_id = request.GET.get('data_id')
    stock = order_models.get_model_obj_by_pk(order_models.StockBatch, data_id)
    out_order_id = stock.stock_batch_id
    code_data = order_models.ItemQRCode. \
        get_stock_batch_info_by_stock_batch_id(out_order_id)
    return my_render(
        request,
        'order/a_jm_stock_batch_info.html',
        code_data = code_data
    )