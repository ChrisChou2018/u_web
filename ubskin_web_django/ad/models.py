import time

from django.db import models
from django.core.paginator import Paginator
from django.db.models import Q
from django.db.models import Count
from django.utils.functional import lazy

from ubskin_web_django.common import common


class Campaigns(models.Model):
    '''
    活动表
    '''
    campaign_id = models.AutoField(db_column="campaign_id", primary_key=True, verbose_name="活动ID")
    location = models.CharField(db_column="location", verbose_name="活动位置", max_length=255)
    campaign_name = models.CharField(db_column="campaign_name", verbose_name="活动名字", max_length=255)
    start_time = models.IntegerField(db_column="start_time", verbose_name="活动开始时间")
    end_time = models.IntegerField(db_column="end_time", verbose_name="活动结束时间")
    intorduction = models.CharField(db_column="intorduction", verbose_name="活动介绍", max_length=1000, null=True, blank=True)
    campaigns_photo_id = models.CharField(db_column="campaigns_photo_id", verbose_name="活动图片ID", max_length=255, null=True, blank=True)
    title_photo_id = models.CharField(db_column="title_photo_id", verbose_name="活动内顶部图片ID", max_length=255, null=True, blank=True)
    status = models.CharField(db_column="status", verbose_name="数据状态", default="normal", max_length=255)
    create_time = models.IntegerField(db_column="create_time", verbose_name="活动创建时间", default=int(time.time()))


    class Meta:
        db_table = "campaigns"

    
    @classmethod
    def get_all_location_list(cls):
        data = cls.objects.filter(status='normal').values('location').annotate(c=Count('location'))
        data = list(data)
        return data

    @classmethod
    def get_campaigns_selecet_all(cls):
        data_list = list()
        data = lazy(cls.objects.filter(status='normal').values('location').annotate(c=Count('location')))
        for i in data:
            o = cls.objects.filter(location=i['location'], status='normal').values("campaign_id", "campaign_name")
            for j in o:
                j['campaign_name'] = i['location'] + '__' + j['campaign_name']
            data_list.extend(o)
        return data_list
    
    @classmethod
    def get_campaigns_tuples_all(cls):
        o = lazy(cls.objects.filter(status='normal').values_list("campaign_id", "campaign_name"))
        return o
        
    @classmethod
    def get_campaigns_by_l_and_d(cls, location, datetime):
        data_list = cls.objects.filter(
            location=location, start_time__lte=datetime, end_time__gte=datetime
        ).values()
        for i in data_list:
            i['campaigns_photo'] = common.build_photo_url(i['campaigns_photo_id'], pic_version='title', cdn=True)
            i['title_photo'] = common.build_photo_url(i['title_photo_id'], pic_version='title', cdn=True)
        return list(data_list)
        


class CampaignItems(models.Model):
    '''
    活动相关商品表
    '''
    campaign_items_id = models.AutoField(db_column="campaign_items_id", primary_key=True, verbose_name="活动商品ID")
    campaign_id = models.BigIntegerField(db_column="campaign_id", verbose_name="活动ID")
    item_id = models.BigIntegerField(db_column="item_id", verbose_name="商品ID")
    status = models.CharField(db_column="status", verbose_name="数据状态", default="normal", max_length=255)
    create_time = models.IntegerField(db_column="create_time", verbose_name="活动创建时间", default=int(time.time()))


    class Meta:
        db_table = "campaign_items"
    

    @classmethod
    def clean_campaigns_for_item_id(cls, item_id):
        cls.objects.filter(item_id=item_id, status='normal').update(status='deleted')
    
    @classmethod
    def get_all_campaign_id_list_by_item_id(cls, item_id):
        data = cls.objects.filter(item_id=item_id, status='normal').values_list('campaign_id')
        data_list = [ i[0] for i in data]
        return data_list
    
    @classmethod
    def get_all_item_id_list_by_campaign_id(cls, campaign_id):
        data = cls.objects.filter(campaign_id=campaign_id, status='normal').values_list('item_id')
        data_list = [ i[0] for i in data]
        return data_list
    

def create_model_data(model, data):
    return model.objects.create(**data)

def update_models_by_pk(model, pk, data):
    model.objects.filter(pk=pk).update(**data)

def get_data_list(model, current_page, search_value=None, order_by="-pk", search_value_type='dict'):
    if search_value:
        if search_value_type == 'dict':
            data_list = model.objects.filter(**search_value, status='normal'). \
                order_by(order_by)
        else:
            data_list = model.objects.filter(search_value, status='normal'). \
                order_by(order_by)
    else:
        data_list = model.objects.filter(status='normal'). \
            order_by(order_by)
    p = Paginator(data_list, 15)
    return p.page(current_page).object_list.values()

def get_data_count(model, search_value=None, search_value_type='dict'):
    if search_value:
        if search_value_type == 'dict':
            count = model.objects.filter(**search_value, status='normal').count()
        else:
            count = model.objects.filter(search_value, status='normal').count()
    else:
        count = model.objects.filter(status='normal').count()
    return count

def get_model_obj_by_pk(model, pk):
    try:
        return model.objects.get(pk=pk)
    except model.DoesNotExist:
        return None