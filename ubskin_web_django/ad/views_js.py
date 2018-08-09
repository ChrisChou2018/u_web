from django.shortcuts import render
from django.http import JsonResponse

from ubskin_web_django.ad import models as ad_models



def delete_campaigns(request):
    return_value = {
        'status':'error',
        'message':'',
    }
    if request.method == 'POST':
        data_id_list = request.POST.getlist('data_id_list[]')
        for i in data_id_list:
            ad_models.update_models_by_pk(
                ad_models.Campaigns,
                i,
                {'status': 'deleted'}
            )
        return_value['status'] = 'success'
        return JsonResponse(return_value)
        