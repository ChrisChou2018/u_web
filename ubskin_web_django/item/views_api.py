import os
import random
import json
import time

from django.views.decorators.csrf import csrf_exempt
from django import forms
from django.http import JsonResponse
from django.conf import settings
from django.forms.models import model_to_dict

from ubskin_web_django.common import photo
from ubskin_web_django.common import decorators
from ubskin_web_django.item import models as item_models
from ubskin_web_django.member import models as member_models
from ubskin_web_django.common import lib_data
from ubskin_web_django.common import common


@decorators.wx_api_authenticated
def get_item_list(request):
    return_value  = {
        'status': 'error',
        'message': '',
        'data': '',
    }
    if request.method == 'GET':
        current_page = request.GET.get('page', 1)
        items = item_models.Items.get_items_list_for_api(current_page)
        return_value['status'] = 'success'
        return_value['data'] = items
        return JsonResponse(return_value)

def get_item_info(request, item_id):
    return_value = {
        'status': 'error',
        'message': ''
    }
    if  request.method == 'GET':
        item_obj = item_models.get_model_obj_by_pk(
            item_models.Items,
            item_id
        )
        if item_obj:
            item_dict = model_to_dict(item_obj)
            item_image = list(
                item_models. \
                    ItemImages.get_item_images_by_itemid(item_dict['item_id'])
            )
            item_info_image = item_models.ItemImages. \
                get_item_info_images_by_itemid(item_dict['item_id'])
            
            if item_image:
                for i in item_image:
                    i['image_path'] = common.build_photo_url(
                        i['photo_id'],
                        pic_version="title",
                        cdn=True
                    )
                item_dict['item_image'] = item_image
            
            if item_info_image:
                item_info_image['image_path'] = common.build_photo_url(
                    item_info_image['photo_id'],
                    pic_version="item",
                    cdn=True
                )
                item_dict['item_info_image'] = item_info_image
            return_value['status'] = 'success'
            return_value['data'] = item_dict
            return JsonResponse(return_value)
        else:
            return_value['message'] = "无次商品信息"
            return JsonResponse(return_value)

@csrf_exempt
def get_item_info_list(request):
    return_value = {
        'status': 'error',
        'message': ''
    }
    if  request.method == 'POST':
        data = json.loads(request.body)
        data_list = list()
        item_id_list = data.get('item_id_list')
        for i in item_id_list:
            item_obj = item_models.get_model_obj_by_pk(
                item_models.Items,
                i
            )
            if item_obj:
                item_dict = model_to_dict(item_obj)
                item_dict['image_path'] = common.build_photo_url(item_dict['photo_id'], cdn=True)
                data_list.append(item_dict)
        return_value['status'] = 'success'
        return_value['data'] = data_list
        return JsonResponse(return_value)

def api_get_categories(request):
    return_value  = {
        'status': 'error',
        'message': '',
        'data': '',
    }
    if request.method == 'GET':
        data_list = item_models.Categories.get_categoreis_for_api()
        return_value['status'] = 'success'
        return_value['data'] = data_list
        return JsonResponse(return_value)

def filter_items(request):
    return_value  = {
        'status': 'error',
        'message': '',
        'data': '',
    }
    if request.method == 'GET':
        categorie_id = request.GET.get('categorie_id')
        current_page = request.GET.get('page', 1)
        datas = item_models.Items. \
            get_items_by_categorie_id(categorie_id, current_page)
        return_value['status'] = 'success'
        return_value['data'] = datas
        return JsonResponse(return_value)

def get_item_comment(request):
    return_value  = {
        'status': 'error',
        'message': '',
        'data': '',
    }
    if request.method == 'GET':
        item_id = request.GET.get('item_id', 1)
        current_page = request.GET.get('page', 1)
        item_comment_data = item_models.ItemComments. \
            get_item_comment_by_item_id(item_id, current_page)
        return_value['status'] = 'success'
        return_value['data'] = item_comment_data
        return JsonResponse(return_value)


@csrf_exempt
@decorators.wx_api_authenticated
def create_item_comment(request):
    return_value = {
        'status': 'error',
        'message': '',
        'data': '',
    }
    request_args = [
        'item_id', 'stars', 'comment_content', 'is_hide'
    ]
    if request.method == 'POST':
        json_data = request.body
        json_data = json.loads(json_data)
        data = {  i: json_data.get(i) for i in request_args }
        openid = request.COOKIES.get('openid')
        member = member_models.Member.get_member_by_wx_openid(openid)
        data.update({'member_id': member.member_id})
        obj = item_models.create_model_data(
            item_models.ItemComments,
            data
        )
        return_value['status'] = 'success'
        return_value['data'] = {'comment_id': obj.comment_id}
        return JsonResponse(return_value)

@csrf_exempt
@decorators.wx_api_authenticated
def upload_cmmment_image(request):
    return_value = {
        'status': 'error',
        'message': '',
        'data': '',
    }
    if request.method == "POST":
        comment_id = request.POST.get('comment_id')
        files = request.FILES
        comment_image_list = []
        if files:
            for i in files:
                file_obj = files[i]
                if not os.path.exists(settings.MEDIA_ROOT,):
                    os.makedirs(settings.MEDIA_ROOT,)
                data = photo.save_upload_photo(
                    file_obj,
                    settings.MEDIA_ROOT,
                )
                if data:
                    data['comment_id'] = comment_id
                    comment_image_list.append(data)
            else:
                item_models.CommentImages. \
                create_many_comment_image(comment_image_list)
                return_value['status'] = 'success'
                return JsonResponse(return_value)

def get_item_info_by_code(request):
    return_value = {
        'status': 'error',
        'message': '',
    }
    if request.method == 'GET':
        item_barcode = request.GET.get('item_barcode')
        if not item_barcode:
            return_value['message'] = '无效的商品码'
            return JsonResponse(return_value)
        item_dict = item_models.Items.get_item_dict_by_barcode_api(item_barcode)
        if item_dict is None:
            return_value['message'] = '没有找到相关的商品'
            return JsonResponse(return_value)
        return_value['status'] = 'success'
        return_value['data'] = [item_dict,]
        return JsonResponse(return_value)

@csrf_exempt
@decorators.wx_api_authenticated
def shopping_cart(request):
    return_value = {
        'status': 'error',
        'message': '',
    }
    openid = request.COOKIES.get('openid')
    member = member_models.Member.get_member_by_wx_openid(openid)
    shopping_cart_obj = item_models.ShoppingCart. \
        get_shopping_cart_by_member_id(member.member_id)
    if request.method == 'GET':
        if shopping_cart_obj:
            shopping_cart_info = shopping_cart_obj.shopping_cart_info
            shopping_cart_info = json.loads(shopping_cart_info)
            data_list = list()
            for i in shopping_cart_info:
                data_list.append({
                    'item_id': i,
                    'item_name': shopping_cart_info[i]['item_name'],
                    'price': shopping_cart_info[i]['price'],
                    'item_num': shopping_cart_info[i]['item_num'],
                    'item_thumbicon': shopping_cart_info[i]['item_thumbicon'],
                })
            return_value['status'] = 'success'
            return_value['data'] = data_list
            return JsonResponse(return_value)
        else:
            return_value['status'] = 'success'
            return_value['data'] = []
            return JsonResponse(return_value)
    
    else:
        data = json.loads(request.body)
        shopping_cart_info = data.get('shopping_cart_info')
        post_type = data.get('post_type')
        if not shopping_cart_info:
            return_value['message'] = '提交数据缺失，请重试'
            return JsonResponse(return_value)
        if not shopping_cart_obj:
            item_models.create_model_data(
                item_models.ShoppingCart,
                {'member_id': member.member_id,
                'shopping_cart_info': json.dumps(shopping_cart_info),
                'create_time': int(time.time(),)}
            )
            return_value['status'] = 'success'
            return JsonResponse(return_value)
        else:
            db_shopping_cart_info = shopping_cart_obj.shopping_cart_info
            db_shopping_cart_info = json.loads(db_shopping_cart_info)
            if post_type == 'add':
                for key in shopping_cart_info:
                    if key not in db_shopping_cart_info:
                        db_shopping_cart_info[key] = shopping_cart_info[key]
                    else:
                        db_shopping_cart_info[key]['item_num'] += shopping_cart_info[key]['item_num']
                if len(db_shopping_cart_info) > 30:
                    return_value['message'] = '购物车已满，请先结算'
                    return JsonResponse(return_value)
                shopping_cart_obj.shopping_cart_info = json.dumps(db_shopping_cart_info)
                shopping_cart_obj.save()
                return_value['status'] = 'success'
                return JsonResponse(return_value)
            elif post_type == 'update':
                for i in shopping_cart_info:
                    db_shopping_cart_info[i]['item_num'] = shopping_cart_info[i]['item_num']
                shopping_cart_obj.shopping_cart_info = json.dumps(db_shopping_cart_info)
                shopping_cart_obj.save()
                return_value['status'] = 'success'
                return JsonResponse(return_value)
            elif post_type == 'delete':
                for i in shopping_cart_info:
                    db_shopping_cart_info.pop(i)
                shopping_cart_obj.shopping_cart_info = json.dumps(db_shopping_cart_info)
                shopping_cart_obj.save()
                return_value['status'] = 'success'
                return JsonResponse(return_value)

            