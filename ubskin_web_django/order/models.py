import time

from django.db import models
from django.forms.models import model_to_dict
from django.core.paginator import Paginator
# Create your models here.



class Order(models.Model):
    order_id                = models.AutoField(db_column='order_id', primary_key=True, verbose_name='order_id')
    out_order_id            = models.CharField(db_column="out_order_id", verbose_name='出库单号', max_length=255)
    recv_code               = models.CharField(db_column="recv_code", verbose_name='到达商家地点代码', max_length=255)
    create_time             = models.IntegerField(db_column="create_time", verbose_name="创建时间", default=int(time.time()))
    status                  = models.CharField(db_column="status", default='normal', max_length=255)


    class Meta:
        db_table = 'order'

class ItemQRCode(models.Model):
    qr_code_id = models.AutoField(db_column='qr_code_id', primary_key=True, verbose_name='qr_code_id')
    qr_code = models.CharField(db_column='qr_code', verbose_name='商品二维码', max_length=255)
    item_barcode = models.CharField(db_column='item_barcode', verbose_name='商品条码', max_length=255)
    out_order_id = models.CharField(db_column='out_order_id', verbose_name='出库单号ID', max_length=255)
    out_status = models.CharField(db_column='out_status', verbose_name='出库状态（out:出库中，in:到达商店）', max_length=255, default='out')
    status = models.CharField(db_column="status", default='normal', max_length=255)
    
    @classmethod
    def get_count_by_out_order_id(cls, out_order_id):
        return cls.objects.filter(out_order_id=out_order_id, status='normal').count()


    class Meta:
        db_table = 'item_qr_code'


class Recv(models.Model):
    recv_id = models.AutoField(db_column='recv_id', primary_key=True, verbose_name='recv_id')
    recv_code = models.CharField(db_column='recv_code', verbose_name='收货方代码', max_length=255)
    recv_addr = models.CharField(db_column='recv_addr', verbose_name='收货地点名称', max_length=255)
    is_watch = models.BooleanField(db_column='is_watch', verbose_name='重点关注', default=False)
    status = models.CharField(db_column="status", default='normal', max_length=255)


    @classmethod
    def get_recv_addr_by_recv_code(cls, recv_code):
        try:
            return cls.objects.get(recv_code=recv_code).recv_addr
        except cls.DoesNotExist:
            return None


    class Meta:
        db_table = 'recv'



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
    model.objects.create(**data)

def delete_models_by_pk(model, id_list):
    model.objects.filter(pk__in=id_list).update(status='deleted')

def update_models_by_pk(model, pk, data):
    model.objects.filter(pk=pk).update(**data)

def get_model_obj_by_pk(model, pk):
    try:
         return model.objects.get(pk=pk)
    except model.DoesNotExist:
        return None