import time

from django.shortcuts import render
from django.http import JsonResponse

from ubskin_web_django.ad import models as ad_models
from ubskin_web_django.item import models as item_models



def get_campaigns(request):
    return_value = {
        'status':'error',
        'message':'',
    }
    if request.method == "GET":
        get = request.GET.get
        location = get('location')
        datetime = get('datetime')
        # datetime = time.strptime(datetime, r"%Y-%m-%d")
        # datetime = int(time.mktime(datetime))
        datetime = int(datetime)
        data_list = ad_models.Campaigns.get_campaigns_by_l_and_d(location, datetime)
        return_value['status'] = 'success'
        return_value['data'] = data_list
        return JsonResponse(return_value)


def get_items_by_campaign_id(request):
    return_value = {
        'status':'error',
        'message':'',
    }
    if request.method == 'GET':
        page = request.GET.get('page', 1)
        campaign_id = request.GET.get('campaign_id')
        data_list = item_models.Items.get_items_by_campaign_id(campaign_id, page)
        return_value['status'] = 'success'
        return_value['data'] = data_list
        return JsonResponse(return_value)