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
    def get_recv_list(cls, current_page, search_value):
        current_page = int(current_page)
        if search_value:
            data_list = cls.objects.filter(recv_addr__icontains=search_value).order_by('pk')
        else:
            data_list = cls.objects.filter().order_by('pk')
        p = Paginator(data_list, 20)
        if current_page > p.num_pages:
            return list()
        else:
            return list(p.page(current_page).object_list.values('recv_code', 'recv_addr'))
    
    @classmethod
    def get_recv_obj_by_recv_code(cls, recv_code):
        return cls.objects.filter(recv_code=recv_code).first()

    @classmethod
    def get_recv_all_by_select(cls):
        return cls.objects.filter(status='normal').values_list('recv_code', 'recv_addr')

    class Meta:
        db_table = 'recv'


class StockBatch(models.Model):
    stock_id                = models.AutoField(db_column='stock_id', primary_key=True, verbose_name='stock_id')
    stock_batch_id          = models.CharField(db_column="stock_batch_id", verbose_name='库存单号', max_length=255)
    recv_code               = models.CharField(db_column="recv_code", verbose_name='到达商家地点代码', max_length=255)
    create_time             = models.IntegerField(db_column="create_time", verbose_name="创建时间", default=int(time.time()))
    create_user             = models.BigIntegerField(db_column='create_user', verbose_name='创建用户', null=True, blank=True)
    status                  = models.CharField(db_column="status", default='normal', max_length=255)

    @classmethod
    def get_stock_dict_by_stock_batch_id(cls, stock_batch_id):
        obj = cls.objects.filter(stock_batch_id=stock_batch_id, status='normal').values()
        if obj:
            return obj[0]
        else:
            return None
    
    @classmethod
    def delete_data_by_stock_batch_id(cls, data_id):
        cls.objects.filter(stock_batch_id=data_id).update(status="deleted")
           
    @classmethod
    def check_has_stock_batch_id(cls, stock_batch_id):
        flag = False
        obj = cls.objects.filter(stock_batch_id=stock_batch_id, status='normal').first()
        flag = True if obj else False
        return flag


    class Meta:
        db_table = 'stock_batch'


class StockBatchCount(models.Model):
    stock_batch_count_id    = models.AutoField(db_column='stock_batch_count_id', primary_key=True, verbose_name='stock_batch_count_id')
    stock_batch_id          = models.CharField(db_column="stock_batch_id", verbose_name='库存单号', max_length=255, null=True, blank=True)
    item_barcode            = models.CharField(db_column='item_barcode', verbose_name='商品条码', max_length=255, null=True, blank=True)
    item_count              = models.IntegerField(db_column="item_count", verbose_name="库商品数量", default=0)
    status                  = models.CharField(db_column="status", default='normal', max_length=255)
    

    class Meta:
        db_table = 'stock_batch_count'
    
    
    @classmethod
    def delete_sb_count_by_sb_id(cls, data_id):
        obj = cls.objects.filter(stock_batch_id=data_id)
        data_id_list = None
        if obj:
            data_id_list = [ i.pk for i in obj]
        if data_id_list:
            ItemQRCode.delete_item_qr_code_by_sb_count_id(data_id_list)
        obj.update(status='deleted')
        

    @classmethod
    def get_item_count_by_stock_batch_id(cls, stock_batch_id):
        obj = cls.objects.filter(stock_batch_id=stock_batch_id, status='normal').values_list('item_count')
        count_list = [ i[0] for i in obj ]
        count = sum(count_list)
        return count

    @classmethod
    def get_obj_by_stock_batch_id(cls, stock_batch_id):
        id_list =  cls.objects.filter(stock_batch_id__icontains=stock_batch_id, status='normal').values_list('stock_batch_count_id')
        id_list = [ i[0] for i in id_list]
        return id_list
    
    @classmethod
    def get_stock_batch_count_by_stock_batch_id(cls, stock_batch_id):
        return cls.objects.filter(stock_batch_id=stock_batch_id, status='normal').values()
    

class ItemQRCode(models.Model):
    qr_code_id = models.AutoField(db_column='qr_code_id', primary_key=True, verbose_name='qr_code_id')
    qr_code = models.CharField(db_column='qr_code', verbose_name='商品二维码', max_length=255, null=True, blank=True)
    stock_batch_count_id = models.BigIntegerField(db_column='stock_batch_count_id', verbose_name='出库单表ID', null=True, blank=True)
    batch_qr_code_id = models.BigIntegerField(db_column='batch_qr_code_id', verbose_name='二维码批次ID', null=True, blank=True)
    search_count = models.IntegerField(db_column='search_count', verbose_name='查询次数', default=0)
    create_user = models.BigIntegerField(db_column='create_user', verbose_name='创建用户', null=True, blank=True)
    status = models.CharField(db_column="status", default='normal', max_length=255)


    @classmethod
    def get_count_by_stock_batch_id(cls, stock_batch_id):
        return cls.objects.filter(stock_batch_id=stock_batch_id, status='normal').count()
    
    @classmethod
    def get_count_by_batch_qr_code_id(cls, batch_qr_code_id):
        return cls.objects.filter(batch_qr_code_id=batch_qr_code_id).count()
    
    @classmethod
    def get_qr_code_obj_by_qr_code(cls, qr_code):
        return cls.objects.get_or_create(qr_code=qr_code)
       
    @classmethod
    def get_qr_code_obj_by_q_code(cls, qr_code):
        try:
            return cls.objects.get(qr_code=qr_code)
        except cls.DoesNotExist:
            return None

    @classmethod
    def delete_item_qr_code_by_sb_count_id(cls, data_id_list):
        cls.objects.filter(stock_batch_count_id__in=data_id_list).update(status='deleted')

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

    @classmethod
    def check_has_item_qr_code(cls, item_qr_code):
        obj = cls.objects.filter(qr_code=item_qr_code, status='normal').first()
        return obj
    
    @classmethod
    def delete_data_by_batch_qr_code_id(cls, batch_qr_code_id):
        cls.objects.filter(status='normal', batch_qr_code_id=batch_qr_code_id).update(**{'status': 'deleted'})
    

    @classmethod
    def get_data_list_by_batch_qr_code_id(cls, batch_qr_code_id):
        return cls.objects.filter(status='normal', batch_qr_code_id=batch_qr_code_id).values_list('qr_code')


    class Meta:
        db_table = 'item_qr_code'


class BatchQrCode(models.Model):
    batch_qr_code_id = models.AutoField(db_column='batch_code_id', primary_key=True, verbose_name='二维码批次ID')
    code_count = models.IntegerField(db_column='code_count', verbose_name='二维码数量')
    create_member = models.BigIntegerField(db_column='create_member', verbose_name='创建用户')
    create_time = models.IntegerField(db_column="create_time", verbose_name="创建时间", default=int(time.time()))
    message = models.TextField(db_column="message", verbose_name='备注信息', null=True, blank=True,)
    recv_code = models.CharField(db_column="recv_code", verbose_name='店铺码', max_length=255, null=True, blank=True,)
    status = models.CharField(db_column="status", default='normal', max_length=255)


    class Meta:
        db_table = 'batch_qr_code'


    @classmethod
    def get_style_table_head(cls):
        return dict(
            batch_qr_code_id = 'ID',
            code_count = '二维码数量',
            create_member = '创建用户',
            recv_code = '绑定店铺',
            more = '更多'
        )


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