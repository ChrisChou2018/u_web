import json
import string
import random

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from ubskin_web_django.order import models as order_models
from ubskin_web_django.member import models as member_models


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
        member = member_models.Member.get_member_by_telephone(openid)
        if not member:
            return_value['message'] = '无权限'
            return JsonResponse(return_value)
        order_models.create_model_data(
            order_models.StockBatch,
            {"stock_batch_id": stock_batch_id, "recv_code": recv_code, "create_user": member.member_id}
        )
        for key, item in item_codes_dict.items():
            for i in item:
                order_models.create_model_data(
                    order_models.ItemQRCode,
                    {
                        "item_barcode": key,
                        "qr_code": i,
                        "stock_batch_id": stock_batch_id,
                        "create_user": member.member_id
                    }
                )
        return_value['status'] = 'success'
        return JsonResponse(return_value)