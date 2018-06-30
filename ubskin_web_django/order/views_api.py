import json
import string
import random
import time

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from ubskin_web_django.order import models as order_models
from ubskin_web_django.member import models as member_models
from ubskin_web_django.common import lib_data 


def get_recv(request):
    if request.method == 'GET':
        return_value = {
            'status': 'error',
            'message': '',
        }
        recv_list = order_models.Recv.get_recv_list()
        return_value['status'] = 'success'
        return_value['data'] = recv_list
        return JsonResponse(return_value)

@csrf_exempt
def create_stock_batch_api(request):
    return_value = {
        'status': 'error',
        'message': '',
    }
    if request.method == 'POST':
        stock_batch_id = ''.join(
            random.choice(string.ascii_lowercase + string.digits) \
            for i in range(8)
        )
        while True:
            stock_batch = order_models.StockBatch.get_stock_dict_by_stock_batch_id(stock_batch_id)
            if stock_batch:
                stock_batch_id = ''.join(
                random.choice(string.ascii_lowercase + string.digits) \
                for i in range(8)
                )
            else:
                break
        data = json.loads(request.body)
        recv_code = data.get('shop_id')
        item_codes_dict = data.get('item_codes_dict')
        openid = data.get('openid')
        member = member_models.Member.get_member_by_wx_openid(openid)
        if not member and not member.is_staff:
            return_value['message'] = '无权限'
            return JsonResponse(return_value)
        order_models.create_model_data(
            order_models.StockBatch,
            {
                "stock_batch_id": stock_batch_id,
                "recv_code": recv_code,
                "create_user": member.member_id,
                "create_time": int(time.time()),
            }
        )
        for key, item in item_codes_dict.items():
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
                order_models.create_model_data(
                    order_models.ItemQRCode,
                    {
                        "qr_code": i,
                        "stock_batch_count_id": stock_batch_count.stock_batch_count_id,
                        "create_user": member.member_id
                    }
                )
        return_value['status'] = 'success'
        return JsonResponse(return_value)


def item_code(request, qr_code):
    return_value = {
        'status': 'error',
        'message': '',
    }
    # qr_code = request.GET.get('qr_code')
    if not (len(qr_code) == 9 and qr_code.startswith('U')):
        return_value['message'] = '商品码格式错误'
        return JsonResponse(return_value)
    
    qr_code_obj = order_models.ItemQRCode.get_qr_code_obj_by_qr_code(qr_code)
    if not qr_code_obj:
        return_value['message'] = '没有记录'
        return JsonResponse(return_value)
    stock_batch_count_id = qr_code_obj.stock_batch_count_id
    obj = order_models.get_model_obj_by_pk(
        order_models.StockBatchCount,
        stock_batch_count_id,
    )
    stock_batch_dict = order_models.StockBatch.get_stock_dict_by_stock_batch_id(obj.stock_batch_id)
    recv_code = stock_batch_dict.get('recv_code')
    recv_addr = order_models.Recv.get_recv_addr_by_recv_code(recv_code)
    date = stock_batch_dict.get('create_time')
    date = lib_data.parse_timestamps(date)
    member_obj = member_models.Member.get_member_by_id(stock_batch_dict.get('create_user'))
    if member_obj:
        is_admin = member_obj.is_admin
        action = "出库扫码" if is_admin else '店铺扫码'
    else:
        action = '店铺扫码'
    return_value['data'] = [
        {"action": action, "to": recv_addr, "date": date},
    ]
    return_value["status"] = "success"
    return JsonResponse(return_value)


