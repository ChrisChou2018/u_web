import json
import string
import random
import time

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from ubskin_web_django.order import models as order_models
from ubskin_web_django.member import models as member_models
from ubskin_web_django.item import models as item_models
from ubskin_web_django.common import lib_data 
from ubskin_web_django.common import decorators
from ubskin_web_django.common import common


def get_recv(request):
    if request.method == 'GET':
        return_value = {
            'status': 'error',
            'message': '',
        }
        current_page = request.GET.get('page', 1)
        value = request.GET.get('search_value')
        recv_list = order_models.Recv.get_recv_list(current_page, value)
        return_value['status'] = 'success'
        return_value['data'] = recv_list
        return JsonResponse(return_value)

@csrf_exempt
@decorators.wx_api_authenticated
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
        openid = request.COOKIES.get('openid')
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
                "create_time": int(timezone.now().timestamp()),
            }
        )
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
                qr_code_obj.stock_batch_count_id = stock_batch_count.stock_batch_count_id
                qr_code_obj.create_user = member.member_id
            else:
                qr_code_obj.save()
                
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
    qr_code_obj.search_count += 1
    qr_code_obj.save()
    batch_qr_code_id = qr_code_obj.batch_qr_code_id
    batch_qr_code_obj = order_models.get_model_obj_by_pk(
        order_models.BatchQrCode,
        batch_qr_code_id
    )
    if not qr_code_obj.stock_batch_count_id and batch_qr_code_obj.recv_code:
        recv_addr = order_models.Recv.get_recv_addr_by_recv_code(batch_qr_code_obj.recv_code)
        date = batch_qr_code_obj.create_time
        date = lib_data.parse_timestamps(date)
        member_obj = member_models.Member.get_member_by_id(batch_qr_code_obj.create_member)
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
    elif not qr_code_obj.stock_batch_count_id and not batch_qr_code_obj.recv_code:
        return_value['messge'] = "该二维码未绑定"
        return JsonResponse(return_value)
    stock_batch_count_id = qr_code_obj.stock_batch_count_id
    obj = order_models.get_model_obj_by_pk(
        order_models.StockBatchCount,
        stock_batch_count_id,
    )
    item_obj = item_models.Items.get_item_obj_by_barcode(obj.item_barcode)
    item_name = '未查询到相关商品信息'
    brand_name = '未查询到相关品牌信息'
    item_photo = common.build_photo_url(None, pic_version='title', cdn=True)
    if item_obj:
        item_name = item_obj.item_name
        brand_id = item_obj.brand_id
        item_photo = common.build_photo_url(item_obj.photo_id, pic_version='title', cdn=True)
        if brand_id:
            brand_obj = item_models.Brands.get_brand_by_id(brand_id)
            brand_name = brand_obj.cn_name if brand_obj else brand_name
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
        {
            "action": action, "to": recv_addr, "date": date,
            'item_name': item_name, 'brand_name': brand_name, 'image': item_photo,
        },
    ]
    return_value["status"] = "success"
    return JsonResponse(return_value)


def check_has_item_qr_code(request):
    return_value = {
        'status': 'error',
        'message': '',
    }
    if request.method == 'GET':
        item_qr_code = request.GET.get('item_qr_code')
        if not (len(item_qr_code) == 9 and item_qr_code.startswith('U')):
            return_value['message'] = '当前二维码无效'
            return JsonResponse(return_value)
        has = order_models.ItemQRCode.check_has_item_qr_code(item_qr_code)
        if not has:
            return_value['message'] = '当前二维码无效'
            return JsonResponse(return_value)
        elif has.stock_batch_count_id:
            return_value['message'] = '当前二维码已被绑定'
            return JsonResponse(return_value)
        else:
            return_value['status'] = 'success'
            return JsonResponse(return_value)