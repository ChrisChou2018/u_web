import time

from django.db import models
from django.forms.models import model_to_dict
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.db.models import Count

from ubskin_web_django.item import models as item_model
# Create your models here.

class Recv(models.Model):
    recv_id = models.AutoField(db_column='recv_id', primary_key=True, verbose_name='recv_id')
    recv_code = models.CharField(db_column='recv_code', verbose_name='收货方代码', max_length=255)
    recv_addr = models.CharField(db_column='recv_addr', verbose_name='收货地点名称', max_length=255)
    is_watch = models.BooleanField(db_column='is_watch', verbose_name='重点关注', default=False)
    status = models.CharField(db_column="status", default='normal', max_length=255)

    @classmethod
    def get_recv_addr_by_recv_code(cls, recv_code):
        try:
            return cls.objects.get(recv_code=recv_code, status='normal').recv_addr
        except cls.DoesNotExist:
            return None
    
    @classmethod
    def get_recv_list(cls, current_page=None):
        current_page = int(current_page)
        data_list = cls.objects.all().order_by('pk')
        p = Paginator(data_list, 20)
        if current_page > p.num_pages:
            return list()
        else:
            return list(p.page(current_page).object_list.values('recv_code', 'recv_addr'))
    
    @classmethod
    def get_recv_obj_by_recv_code(cls, recv_code):
        return cls.objects.filter(recv_code=recv_code).first()


    class Meta:
        db_table = 'recv'


class StockBatch(models.Model):
    stock_id                = models.AutoField(db_column='stock_id', primary_key=True, verbose_name='stock_id')
    stock_batch_id          = models.CharField(db_column="stock_batch_id", verbose_name='库存单号', max_length=255)
    recv_code               = models.CharField(db_column="recv_code", verbose_name='到达商家地点代码', max_length=255)
    create_time             = models.IntegerField(db_column="create_time", verbose_name="创建时间", default=int(time.time()))
    status                  = models.CharField(db_column="status", default='normal', max_length=255)
    create_user             = models.BigIntegerField(db_column='create_user', verbose_name='创建用户', null=True, blank=True)

    @classmethod
    def get_stock_dict_by_stock_batch_id(cls, stock_batch_id):
        obj = cls.objects.filter(stock_batch_id=stock_batch_id, status='normal').values()
        if obj:
            return obj[0]
        else:
            return None


    class Meta:
        db_table = 'stock_batch'


class StockBatchCount(models.Model):
    stock_batch_count_id    = models.AutoField(db_column='stock_batch_count_id', primary_key=True, verbose_name='stock_batch_count_id')
    stock_batch_id          = models.CharField(db_column="stock_batch_id", verbose_name='库存单号', max_length=255, null=True, blank=True)
    item_barcode            = models.CharField(db_column='item_barcode', verbose_name='商品条码', max_length=255, null=True, blank=True)
    item_count              = models.IntegerField(db_column="item_count", verbose_name="库商品数量", default=0)

    class Meta:
        db_table = 'stock_batch_count'

    @classmethod
    def get_item_count_by_stock_batch_id(cls, stock_batch_id):
        obj = cls.objects.filter(stock_batch_id=stock_batch_id).values_list('item_count')
        count_list = [ i[0] for i in obj ]
        count = sum(count_list)
        return count

    @classmethod
    def get_obj_by_stock_batch_id(cls, stock_batch_id):
        id_list =  cls.objects.filter(stock_batch_id=stock_batch_id).values_list('stock_batch_count_id')
        id_list = [ i[0] for i in id_list]
        return id_list
    
    @classmethod
    def get_stock_batch_count_by_stock_batch_id(cls, stock_batch_id):
        return cls.objects.filter(stock_batch_id=stock_batch_id).values()

class ItemQRCode(models.Model):
    qr_code_id = models.AutoField(db_column='qr_code_id', primary_key=True, verbose_name='qr_code_id')
    qr_code = models.CharField(db_column='qr_code', verbose_name='商品二维码', max_length=255, null=True, blank=True)
    stock_batch_count_id = models.BigIntegerField(db_column='stock_batch_count_id', verbose_name='出库单表ID', null=True, blank=True)
    status = models.CharField(db_column="status", default='normal', max_length=255)
    create_user = models.BigIntegerField(db_column='create_user', verbose_name='创建用户', null=True, blank=True)


    @classmethod
    def get_count_by_stock_batch_id(cls, stock_batch_id):
        return cls.objects.filter(stock_batch_id=stock_batch_id, status='normal').count()
    
    @classmethod
    def get_qr_code_obj_by_qr_code(cls, qr_code):
        try:
            return cls.objects.filter(qr_code=qr_code).first()
        except cls.DoesNotExist:
            return None

    @classmethod
    def get_stock_batch_info_by_stock_batch_id(cls, stock_batch_id):
        data_dict = dict()
        stock = StockBatch.get_stock_dict_by_stock_batch_id(stock_batch_id)
        recv_addr = Recv.get_recv_addr_by_recv_code(stock['recv_code'])
        data_dict['stock_batch_id'] = stock_batch_id
        data_dict['recv_addr'] = recv_addr
        data_dict['recv_code'] = stock['recv_code']
        obj = StockBatchCount.get_stock_batch_count_by_stock_batch_id(stock_batch_id)
        data_dict['item_code_list'] = obj
        if data_dict['item_code_list']:
            for i in data_dict['item_code_list']:
                i['item_name'] = item_model.Items.get_item_name_by_barcode(i['item_barcode'])
        data_dict['all_count'] = StockBatchCount.get_item_count_by_stock_batch_id(stock_batch_id)
        return data_dict


    class Meta:
        db_table = 'item_qr_code'


def get_data_list(model, current_page, search_value=None, order_by="-pk"):
    if search_value:
        data_list = model.objects.filter(**search_value, status='normal'). \
            order_by(order_by)
    else:
        data_list = model.objects.filter(status='normal'). \
            order_by(order_by)
    p = Paginator(data_list, 15)
    return p.page(current_page).object_list.values()

def get_data_count(model, search_value=None):
    if search_value:
        count = model.objects.filter(**search_value, status='normal').count()
    else:
        count = model.objects.filter(status='normal').count()
    return count   

def create_model_data(model, data):
     return model.objects.create(**data)

def delete_models_by_pk(model, id_list):
    model.objects.filter(pk__in=id_list).update(status='deleted')

def update_models_by_pk(model, pk, data):
    model.objects.filter(pk=pk).update(**data)

def get_model_obj_by_pk(model, pk):
    try:
         return model.objects.get(pk=pk)
    except model.DoesNotExist:
        return None