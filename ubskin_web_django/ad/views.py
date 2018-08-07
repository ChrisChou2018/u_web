from django.shortcuts import render

from ubskin_web_django.ad import models as ad_models


def my_render(request, templater_path, **kwargs):
    return render(request, templater_path, dict(**kwargs))

def campaigns_manage(request):
    search_dict = {
        'search_value': 'campaign_name__icontains',
    }
    search_value = dict()
    current_page = request.GET.get('page', 1)
    filter_args = '&'
    for i in search_dict:
        value = request.GET.get(i)
        if value is not None:
            search_value[search_dict[i]] = value
            filter_args += "{}={}".format(i, value)
    else:
        if len(filter_args) == 1:
            filter_args = None
    if search_value:
        data_list = ad_models.get_data_list(
            ad_models.Campaigns,
            current_page,
            search_value=search_value
        )
        data_count = ad_models.get_data_count(
            ad_models.Campaigns,
            search_value,
        )
    else:
        data_list = ad_models.get_data_list(
            ad_models.Campaigns,
            current_page,
        )
        data_count = ad_models.get_data_count(
            ad_models.Campaigns,
        )

    return my_render(
        request,
        'ad/a_campaigns_manage.html',
        current_page = current_page,
        form_data = request.GET,
        filter_args = filter_args,
        data_list = data_list,
        data_count = data_count,
    )

def add_campaigns(request):
    pass

def editor_campaigns(request):
    pass