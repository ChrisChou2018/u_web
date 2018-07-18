import time

from django.db import models
from django.core.paginator import Paginator
from django.forms import model_to_dict
from django.conf import settings
from django.db.models import Q

from ubskin_web_django.member import models as member_models
from ubskin_web_django.common import common



class Brands(models.Model):
    '''
    品牌表
    '''
    brand_id                    = models.AutoField(db_column="brand_id", primary_key=True, verbose_name="品牌ID")
    cn_name                     = models.CharField(db_column="cn_name", verbose_name="品牌中文名", max_length=255)
    cn_name_abridge             = models.CharField(db_column="cn_name_abridge", null=True, blank=True, verbose_name="品牌中文名缩写", max_length=255)
    en_name                     = models.CharField(db_column="en_name", null=True, blank=True, verbose_name="品牌英文名", max_length=255)
    form_country                = models.CharField(db_column="form_country", null=True, blank=True, verbose_name="所属国家", max_length=255)
    key_word                    = models.CharField(db_column="key_word", null=True, blank=True, verbose_name="搜索关键字", max_length=255)
    brand_about                 = models.CharField(db_column="brand_about", null=True, blank=True, verbose_name="品牌简介", max_length=255)
    photo_id                    = models.CharField(db_column="photo_id", null=True, blank=True, verbose_name='图片名', max_length=255)
    status                      = models.CharField(db_column="status", verbose_name="状态", default="normal", max_length=255)

    @classmethod
    def get_brands_dict_for_all(cls):
        all_data = cls.objects.all().values_list('brand_id','cn_name')
        return dict(all_data)

    @classmethod
    def get_brand_by_id(cls, brand_id):
        try:
            return cls.objects.get(pk = brand_id)
        except cls.DoesNotExist:
            return None
    
    @classmethod
    def update_brand_by_id(cls, brand_id, data):
        cls.objects.filter(pk = brand_id).update(**data)
    
    @classmethod
    def delete_brands_by_id_list(cls, id_list):
        cls.objects.filter(pk__in = id_list).delete()


    class Meta:
        db_table = "brands"


class Items(models.Model):
    '''
    商品表
    '''
    item_id                     = models.AutoField(db_column="item_id", primary_key=True, verbose_name='商品ID')
    item_name                   = models.CharField(db_column="item_name", verbose_name='商品名称', max_length=255)
    item_info                   = models.CharField(db_column="item_info", null=True, blank=True, verbose_name='商品信息', max_length=255)
    item_code                   = models.CharField(db_column="item_code", null=True, blank=True, verbose_name="商品编码", max_length=255)
    item_barcode                = models.CharField(db_column="item_barcode", null=True, blank=True, verbose_name="商品条码", max_length=255)
    price                       = models.FloatField(db_column="price", null=True, blank=True, verbose_name="商品售价")
    current_price               = models.FloatField(db_column='current_price', null=True, blank=True, verbose_name="批发价")
    original_price              = models.FloatField(db_column='original_price', null=True, blank=True, verbose_name="参考价")
    foreign_price               = models.FloatField(db_column='foreign_price', null=True, blank=True, verbose_name="国外价格")
    comment_count               = models.IntegerField(db_column="comment_count", null=True, blank=True, verbose_name="评论数量")
    hot_value                   = models.IntegerField(db_column="hot_value", null=True, blank=True, verbose_name="热度值")
    buy_count                   = models.IntegerField(db_column="buy_count", null=True, blank=True, verbose_name="被购买次数")
    key_word                    = models.CharField(db_column="key_word", null=True, blank=True, verbose_name="搜索关键字", max_length=255)
    origin                      = models.CharField(db_column="origin", null=True, blank=True, verbose_name="生产地", max_length=255)
    shelf_life                  = models.CharField(db_column="shelf_life", null=True, blank=True, verbose_name="保质期", max_length=255)
    capacity                    = models.CharField(db_column="capacity", null=True, blank=True, verbose_name="规格", max_length=255)
    specifications_type_choices = (
        (0, '瓶'),
        (1, '包'),
        (2, '套'),
        (3, '片'),
        (4, '支'),
        (5, '袋'),
        (6, '对'),
        (7, '盒'),
        (8, '个'),
        (9, '罐'),
    )
    specifications_type_id      = models.SmallIntegerField(db_column="specifications_type_id", choices=specifications_type_choices, null=True, blank=True, verbose_name="单位类型")
    specifications_type         = models.CharField(db_column="specifications_type", null=True, blank=True, verbose_name="单位", max_length=255)
    categorie_id               = models.BigIntegerField(db_column="categorie_id", null=True, blank=True, verbose_name="分类ID")
    brand_id                    = models.BigIntegerField(db_column="brand_id", null=True, blank=True, verbose_name="品牌ID")
    brand_name                  = models.CharField(db_column="brand_name", null=True, blank=True, verbose_name="品牌名", max_length=255)
    for_people                  = models.CharField(db_column="for_people", null=True, blank=True, verbose_name="适用人群", max_length=255)
    weight                      = models.CharField(db_column="weight", null=True, blank=True, verbose_name="重量", max_length=255)
    create_person               = models.CharField(db_column="create_person", verbose_name="创建人", max_length=255)
    create_time                 = models.IntegerField(db_column="create_time", verbose_name="创建时间", default=int(time.time()))
    update_person               = models.CharField(db_column="update_person", null=True, blank=True, verbose_name="更新人", max_length=255)
    update_time                 = models.IntegerField(db_column="update_time", verbose_name="更新时间", default=int(time.time()))
    stock_count                 = models.IntegerField(db_column="stock_count", verbose_name="库存", default=0, null=True, blank=True)
    status                      = models.CharField(db_column="status", verbose_name="状态", default="normal", max_length=255)
    photo_id                    = models.CharField(db_column="photo_id", verbose_name="图片名", max_length=255, null=True, blank=True)
    

    @classmethod
    def create_item(cls, datas):
        cls.objects.create(**datas)

    @classmethod
    def get_item_by_id(cls, item_id):
        try:
            return cls.objects.get(pk=item_id)
        except cls.DoesNotExist:
            return None
    
    @classmethod
    def delete_item_by_item_ids(cls, id_list):
        cls.objects.filter(pk__in=id_list).update(status='deleted')
    
    @classmethod
    def update_item_by_id(cls, item_id, data):
        cls.objects.filter(pk = item_id).update(**data)

    @classmethod
    def get_item_id_by_item_name(cls, item_name):
        l = cls.objects.filter(item_name__icontains = item_name).values_list('item_id')
        if l:
            l = [i[0] for i in l]
            return l
        else:
            return []
    
    @classmethod
    def get_items_list_for_api(cls, current_page):
        '请求商品列表接口'
        item_obj = cls.objects.filter(status = 'normal').order_by('-item_id')
        p = Paginator(item_obj, 15)
        current_page = int(current_page)
        if current_page > p.num_pages:
            return list()
        items_list = p.page(current_page).object_list.values(
            'item_id', "item_name", "price", "stock_count", "photo_id"
        )
        items_list = list(items_list)
        for i in items_list:
            i['item_thumbicon'] = common.build_photo_url(i['photo_id'], cdn=True)
        return items_list
    
    @classmethod
    def get_items_by_categorie_id(cls, categorie_id, current_page):
        item_obj = cls.objects. \
            filter(categorie_id = categorie_id, status = 'normal').order_by('-item_id')
        p = Paginator(item_obj, 15)
        items_list =  list(
            p.page(current_page).object_list.values(
                'item_id', "item_name", "price", "stock_count", "photo_id"
            )
        )
        for i in items_list:
            i['item_thumbicon'] = common.build_photo_url(i['photo_id'], cdn=True)
        return items_list
    
    @classmethod
    def get_item_name_by_barcode(cls, item_barcode):
        obj = cls.objects.filter(item_barcode=item_barcode).first()
        if obj:
            return obj.item_name
        else:
            return None
    
    @classmethod
    def get_item_obj_by_barcode(cls, item_barcode):
        return cls.objects.filter(item_barcode=item_barcode)

    @classmethod
    def get_item_dict_by_item_barcode(cls, item_barcode):
        model = cls.objects.filter(item_barcode=item_barcode).first()
        if model:
            return model_to_dict(model)
        else:
            return {}

    @classmethod
    def get_item_dict_by_barcode_api(cls, item_barcode):
        data_dict = dict()
        model = cls.objects.filter(item_barcode=item_barcode).last()
        if not model:
            return None
        model = model_to_dict(model)
        data_dict['item_name'] = model.get('item_name')
        data_dict['specifications_type'] = model.get('capacity') if model.get('capacity') else '无规格信息'
        data_dict['thumbicon'] = common.build_photo_url(model.get('photo_id'), cdn=True)
        data_dict['item_barcode'] = model.get('item_barcode')
        return data_dict

    @classmethod
    def has_exist_item_code(cls, item_code, item_id):
        obj = cls.objects.filter(item_code=item_code).first()
        if obj and item_id != obj.item_id:
            return True
        else:
            return False
    @classmethod
    def has_exist_item_barcode(cls, item_barcode, item_id):
        obj = cls.objects.filter(item_barcode=item_barcode).first()
        if obj and item_id != obj.item_id:
            return True
        else:
            return False


    class Meta:
        db_table = "items"


class ItemImages(models.Model):
    '''
    商品图片表
    '''
    image_id       = models.AutoField(db_column="image_id", primary_key=True, verbose_name="图片ID")
    item_id        = models.BigIntegerField(db_column="item_id", verbose_name="所属商品ID")
    type_choces    = (
        (0, "item"),
        (1, "item_info"),
    )
    image_type      = models.IntegerField(db_column="image_type", choices=type_choces, verbose_name="图片类型", default=0)
    photo_id        = models.CharField(db_column="photo_id", verbose_name="图片名", max_length=255, null=True, blank=True)
    file_size       = models.CharField(db_column="file_size", verbose_name="文件大小", max_length=255)
    resolution      = models.CharField(db_column="resolution", verbose_name="分辨率", max_length=255)
    file_type       = models.CharField(db_column="file_type", verbose_name="文件类型", max_length=255)
    status          = models.CharField(db_column="status", verbose_name="状态", max_length=255)


    @classmethod
    def get_item_images_by_itemid(cls, item_id):
        image_obj = cls.objects.filter(item_id=item_id, status = "normal", image_type=0).values()
        return image_obj
    
    @classmethod
    def get_item_info_images_by_itemid(cls, item_id):
        image_obj = cls.objects.filter(item_id=item_id, status = "normal", image_type=1).values().first()
        return image_obj
        
    @classmethod
    def create_item_image(cls, datas):
        cls.objects.create(**datas)

    @classmethod
    def update_images_by_image_id_list(cls, image_id_list, item_dict):
        obj_list =  cls.objects.filter(image_id__in = image_id_list)
        obj_list.update(**item_dict)
        item_id_list = obj_list.values_list('item_id')
        item_id_list = [  i[0] for i in item_id_list ]
        Items.objects.filter(item_id__in = item_id_list).update(photo_id=None)


    class Meta:
        db_table = "item_images"


class ItemTags(models.Model):
    '''
    商品标签表
    '''
    tag_id          = models.AutoField(db_column="tag_id", verbose_name="标签ID", primary_key=True)
    tag_name        = models.CharField(db_column="tag_name", verbose_name="标签名", max_length=255)
    item_id         = models.BigIntegerField(db_column="item_id", verbose_name="所属商品ID")
    
    
    class Meta:
        db_table = "item_tags"


class Categories(models.Model):
    '''
    商品分类表
    '''
    categorie_id   = models.AutoField(db_column="categorie_id", verbose_name="分类ID", primary_key=True)
    categorie_name  = models.CharField(db_column="categorie_name", verbose_name="分类名", max_length=255)
    categorie_type  = models.CharField(db_column="categorie_type", null=True, blank=True, verbose_name="类别", max_length=255)
    photo_id        = models.CharField(db_column="photo_id", null=True, blank=True, verbose_name="缩略图路径", max_length=255)
    status          = models.CharField(db_column="status", verbose_name="状态", default="normal", max_length=255)


    @classmethod
    def get_categoreis_dict_for_all(cls):
        all_obj =  cls.objects.all().values_list("categorie_id", "categorie_name")
        return dict(all_obj)

    @classmethod
    def get_list_categories(cls, current_page, search_value=None):
        if search_value:
            obj = cls.objects.filter(**search_value). \
                order_by('-pk')
        else:
            obj = cls.objects.all().order_by('-pk')
        
        p = Paginator(obj, 15)
        return p.page(current_page).object_list.values() 
    
    @classmethod
    def get_categories_count(cls, search_value=None):
        if search_value:
            count = cls.objects.filter(**search_value).count()
        else:
            count = cls.objects.all().count()
        return count
    
    @classmethod
    def get_categorie_by_id(cls, categorie_id):
        try:
            return cls.objects.get(pk=categorie_id)
        except cls.DoesNotExist:
            return None

    @classmethod
    def update_categorie_by_id(cls, categorie_id, data):
        cls.objects.filter(pk=categorie_id).update(**data)

    @classmethod
    def delete_categories_by_id_list(cls, id_list):
        cls.objects.filter(pk__in = id_list).delete()
    
    @classmethod
    def get_categoreis_for_api(cls):
        data_dict = dict()
        for i in cls.type_choices:
            temp = cls.objects.filter(categorie_type = i[0]).values('categorie_id', 'categorie_name', 'photo_id')
            temp = list(temp)
            for j in temp:
                j['image_path'] = common.build_photo_url(j['photo_id'], pic_version='thumbicon', cdn=True)
            data_dict[i[1]] = temp
        # brands = Brands.objects.filter(status='normal').values('brand_id', 'cn_name', 'photo_id')
        # for i in brands:
        #     i['image_path'] = common.build_photo_url(i['photo_id'], pic_version='thumbicon', cdn=True)
        # data_dict['热门品牌'] = list(brands)
        return data_dict


    class Meta:
        db_table = "categories"


class ItemComments(models.Model):
    '''
    商品评论表
    '''
    comment_id      = models.AutoField(db_column="comment_id", verbose_name="评论ID", primary_key=True)
    member_id       = models.BigIntegerField(db_column="member_id", verbose_name="评论用户ID")
    item_id         = models.BigIntegerField(db_column="item_id", verbose_name="所属商品ID")
    comment_content = models.CharField(max_length=255, db_column="comment_content", verbose_name="评论内容")
    create_time     = models.IntegerField(db_column="create_time", verbose_name="创建时间", default=int(time.time()))
    start_choices   = (
        (1, '1星'),
        (2, '2星'),
        (3, '3星'),
        (4, '4星'),
        (5, '5星'),
    ) 
    stars           = models.SmallIntegerField(db_column="stars", choices=start_choices, verbose_name="星级", default=5, blank=True)
    status          = models.CharField(db_column="status", verbose_name="状态", default="normal", max_length=255)

    @classmethod
    def get_item_comments_list(cls, current_page, search_value=None):
        if search_value:
            item_comments_list = cls.objects.filter(
                **search_value, status = 'normal'
            ).order_by('-comment_id')
        else:
            item_comments_list = cls.objects.filter(status = 'normal').order_by('-comment_id')
        p = Paginator(item_comments_list, 15)
        data = p.page(current_page).object_list.values()
        for i in data:
            member_id = i['member_id']
            item_id = i['item_id']
            member_obj = member_models.Member.get_member_by_id(member_id)
            i['member_name'] = member_obj.member_name if member_obj else '已经注销用户'
            item_obj = Items.get_item_by_id(item_id)
            i['item_name'] = item_obj.item_name if item_obj else '商品已经下架'
        return data
    
    @classmethod
    def get_item_comments_count(cls, search_value=None):
        if search_value:
            count = cls.objects.filter(**search_value, status = 'normal').count()
        else:
            count = cls.objects.filter(status = 'normal').count()
        return count

    @classmethod
    def delete_comment_by_id_list(cls, id_list):
        cls.objects.filter(pk__in=id_list).update(status='deleted')

    @classmethod
    def get_item_comment_by_item_id(cls, item_id, current_page):
        try:
            item_comments_list = cls.objects.filter(
                item_id = item_id, status = 'normal'
                ).order_by('-comment_id')
            p = Paginator(item_comments_list, 15)
            data = p.page(current_page).object_list.values()
            data = list(data)
            for i in data:
                image_list = CommentImages.get_comment_image_obj_by_id(i['comment_id'], True)
                i['image_list'] = image_list
            return data
        except cls.DoesNotExist:
            return None
    
    @classmethod
    def get_item_comment_by_id(cls, comment_id):
        try:
            model_obj = cls.objects.get(pk=comment_id)
            return model_to_dict(model_obj)
        except cls.DoesNotExist:
            return None
    
    @classmethod
    def update_item_comment_by_id(cls, comment_id, data):
        cls.objects.filter(pk=comment_id).update(**data)

    class Meta:
        db_table = "item_comments"


class CommentImages(models.Model):
    '''
    评论图片表
    '''
    image_id        = models.AutoField(db_column="image_id", verbose_name="图片ID", primary_key=True)
    comment_id      = models.BigIntegerField(db_column="comment_id", verbose_name="所属评论ID")
    photo_id        = models.CharField(db_column="photo_id", verbose_name="图片名", max_length=255, null=True, blank=True)
    file_size       = models.CharField(db_column="file_size", verbose_name="文件大小", max_length=255)
    resolution      = models.CharField(db_column="resolution", verbose_name="分辨率", max_length=255)
    file_type       = models.CharField(db_column="file_type", verbose_name="文件类型", default='.jpg', max_length=255)
    status          = models.CharField(db_column="status", verbose_name="状态", default="normal", max_length=255)


    @classmethod
    def get_comment_image_obj_by_id(cls, comment_id, for_api=False):
        image_list = list(cls.objects.filter(comment_id = comment_id, status = 'normal').values())
        if for_api:
            for i in image_list:
                i['image_path'] = common.build_photo_url(i['photo_id'], pic_version='title', cdn=True)
        for i in image_list:
                i['image_path'] = common.build_photo_url(i['photo_id'], pic_version='title')
        return image_list
    
    @classmethod
    def create_many_comment_image(cls, data_list):
        for i in data_list:
            cls.objects.create(**i)


    class Meta:
        db_table = "comment_images"


class ShoppingCart(models.Model):
    '''
    购物车表
    '''
    shopping_cart_id        = models.AutoField(db_column="shopping_cart_id", verbose_name="购物车ID", primary_key=True)
    member_id               = models.BigIntegerField(db_column="member_id", verbose_name="用户ID")
    shopping_cart_info      = models.CharField(db_column="item_info", verbose_name="购物车信息(维护一个json字典)", max_length=10000, null=True, blank=True)
    create_time             = models.IntegerField(db_column="create_time", verbose_name="创建时间", default=int(time.time()))
    pay_status              = models.CharField(db_column="pay_status", verbose_name="支付状态", max_length=255, default='not_pay')


    @classmethod
    def get_shopping_cart_by_member_id(cls, member_id):
        return cls.objects.filter(member_id=member_id).first()


    class Meta:
        db_table = "shopping_cart"


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

def create_model_data(model, data):
    return model.objects.create(**data)

def get_model_obj_by_pk(model, pk):
    try:
         return model.objects.get(pk=pk)
    except model.DoesNotExist:
        return None