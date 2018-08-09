import time
import datetime
import os

from django.shortcuts import render
from django.shortcuts import redirect
from django import forms
from django.conf import settings
from django.forms import model_to_dict

from ubskin_web_django.ad import models as ad_models
from ubskin_web_django.item import models as item_models
from ubskin_web_django.common import photo


def my_render(request, templater_path, **kwargs):
    return render(request, templater_path, dict(**kwargs))

def campaigns_manage(request):
    if request.method == "GET":
        search_dict = {
            'search_value': 'campaign_name__icontains',
            'location': 'location',
        }
        search_value = dict()
        current_page = request.GET.get('page', 1)
        filter_args = ""
        for i in search_dict:
            value = request.GET.get(i)
            if value is not None:
                search_value[search_dict[i]] = value
                filter_args  += "&{}={}".format(i, value)
        else:
            if not filter_args:
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
        location_list = ad_models.Campaigns.get_all_location_list()
        return my_render(
            request,
            'ad/a_campaigns_manage.html',
            current_page = current_page,
            form_data = request.GET,
            filter_args = filter_args,
            data_list = data_list,
            data_count = data_count,
            location_list = location_list,
        )

class AddCampaignForm(forms.ModelForm):
    datetime = forms.CharField(error_messages={'required': '至少这个不可以为空'})

    class Meta:
        model = ad_models.Campaigns
        fields = (
            'location', 'campaign_name', 'intorduction'
        )

    def save(self, commit=True):
        model_obj = super(AddCampaignForm, self).save(commit=False)
        if commit:
            datetime = self.cleaned_data['datetime']
            if datetime:
                start_time, end_time = datetime.split(' - ')
                start_time = time.mktime(time.strptime(start_time, r'%m/%d/%Y'))
                end_time = time.mktime(time.strptime(end_time, r'%m/%d/%Y'))
                model_obj.start_time = start_time
                model_obj.end_time = end_time
                model_obj.create_time = int(time.time())
            model_obj.save()
        return model_obj

def add_campaign(request):
    categories_dict = item_models.Categories.get_categoreis_select_for_all()
    if request.method == 'GET':
        return my_render(
            request,
            'ad/a_add_campign.html',
        )
    else:
        form = AddCampaignForm(request.POST)
        if  not form.is_valid():
            print(form.errors)
            return my_render(
                request,
                'ad/a_add_campign.html',
                form_errors = form.errors,
                form_data = request.POST,
                categories_dict = categories_dict,
            )
        model_obj =  form.save()
        files = request.FILES
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
                    setattr(model_obj, i, data['photo_id'])
                    model_obj.save()
        return redirect('/myadmin/campaigns_manage/')


class EditorCampaignForm(forms.ModelForm):


    datetime = forms.CharField(error_messages={'required': '至少这个不可以为空'})


    class Meta:
        model = ad_models.Campaigns
        fields = (
            'location', 'campaign_name', 'intorduction'
        )
    

    def update(self, data_id):
        model = self._meta.model
        data = self.cleaned_data
        datetime = data.pop('datetime')
        start_time, end_time = datetime.split(' - ')
        start_time = time.mktime(time.strptime(start_time, r'%m/%d/%Y'))
        end_time = time.mktime(time.strptime(end_time, r'%m/%d/%Y'))
        data.update({'start_time': start_time, 'end_time': end_time})
        ad_models.update_models_by_pk(
            model,
            data_id,
            data,
        )


def editor_campaign(request):
    data_id = request.GET.get('data_id')
    model_obj = ad_models.get_model_obj_by_pk(
        ad_models.Campaigns,
        data_id
    )
    categories_dict = item_models.Categories.get_categoreis_select_for_all()
    if request.method == "GET":
        if model_obj:
            form_data = model_to_dict(model_obj)
            start_time = form_data.pop('start_time')
            start_time = time.localtime(start_time)
            start_time = time.strftime(r'%m/%d/%Y', start_time)
            end_time = form_data.pop('end_time')
            end_time = time.localtime(end_time)
            end_time = time.strftime(r'%m/%d/%Y', end_time)
            datetime = ' - '.join([start_time, end_time])
            form_data.update({'datetime': datetime})
            return my_render(
                request,
                'ad/a_add_campign.html',
                form_data = form_data,
                categories_dict = categories_dict,
            )
        else:
            return redirect(request.get_full_path().split('back_url=')[1])
    else:
        form = EditorCampaignForm(request.POST)
        if  not form.is_valid():
            return my_render(
                request,
                'ad/a_add_campign.html',
                form_errors = form.errors,
                form_data = request.POST,
            )
        form.update(data_id)
        files = request.FILES
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
                    setattr(model_obj, i, data['photo_id'])
                    model_obj.save()
        return redirect(request.get_full_path().split('back_url=')[1])