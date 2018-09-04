import time

from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser, PermissionsMixin
)
from django.forms.models import model_to_dict
from django.core.paginator import Paginator
from django.db.models import Count
from django.db.models import Q

from ubskin_web_django.item import models as item_models
from ubskin_web_django.common import common


class UserProfileManager(BaseUserManager):
    def create_user(self, user_name, member_name, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not user_name:
            raise ValueError('必须要有用户名')

        user = self.model(
            user_name=user_name,
            member_name=member_name,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, user_name, member_name, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(user_name,
            password=password,
            member_name=member_name
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class Member(AbstractBaseUser, PermissionsMixin):
    member_id           = models.AutoField(db_column="member_id", primary_key=True, verbose_name="用户ID")
    member_name         = models.CharField(db_column="member_name", max_length=255, null=True, blank=True)
    telephone           = models.CharField(db_column="telephone", max_length=255, null=True, blank=True)
    user_name           = models.CharField(db_column="user_name", max_length=255, unique=True, null=True, blank=True)
    wx_openid           = models.CharField(db_column="wx_openid", max_length=255, null=True, blank=True)
    status              = models.CharField(db_column="status", default='normal', max_length=255)
    sessions            = models.CharField(db_column="sessions", max_length=255, null=True, blank=True)
    created_ip          = models.CharField(db_column="created_ip", null=True, blank=True, max_length=255)
    create_time         = models.IntegerField(db_column="create_time", default=int(time.time()))
    update_time         = models.IntegerField(db_column="update_time", default=int(time.time()))
    is_active           = models.BooleanField(default=True)
    is_admin            = models.BooleanField(default=False)
    is_staff            = models.BooleanField(default=True)
    avatar              = models.CharField(db_column="avatar", max_length=255, null=True, blank=True)
    bind_recv           = models.BigIntegerField(db_column="bind_recv", verbose_name='绑定的到货方（店铺）', null=True, blank=True)
    remarks             = models.CharField(db_column="remarks", verbose_name="用户备注", max_length=2000, null=True, blank=True)


    objects = UserProfileManager()
    USERNAME_FIELD = 'user_name'
    REQUIRED_FIELDS = ['member_name']

    def __str__(self):  # __unicode__ on Python 2
        return self.member_name if self.member_name else str(self)
    
    def get_full_name(self):
        return self.member_name

    def get_short_name(self):
        return self.member_name

    @classmethod
    def get_style_table_head(cls):
        return dict(
            member_id = '用户ID',
            member_name = '用户名',
            telephone = '手机号',
            wx_openid = '微信openID',
            is_admin = '管理员身份',
            is_staff = '内部账号',
            more = '更多'
        )

    @classmethod
    def has_member_telephone(cls, telephone, member_id):
        try:
            member =  cls.objects.get(telephone=telephone, status='normal')
            if member and member.member_id != int(member_id):
                return True
            else:
                return False
        except cls.DoesNotExist:
            return False
    
    @classmethod
    def update_member_by_id(cls, member_id, data):
        cls.objects.filter(member_id=member_id).update(**data)

    @classmethod
    def delete_members_by_id_list(cls, id_list):
        cls.objects.filter(member_id__in=id_list).update(status='deleted')

    @classmethod
    def get_member_by_id(cls, member_id):
        try:
            return cls.objects.get(pk=member_id)
        except cls.DoesNotExist:
            return None
    
    @classmethod
    def get_member_by_telephone(cls, telephone):
        try:
            return cls.objects.get(
            telephone = telephone,
            status = 'normal'
            )
        except cls.DoesNotExist:
            return None
    
    @classmethod
    def get_member_by_wx_openid(cls, wx_openid):
        try:
            return cls.objects.get(
            wx_openid = wx_openid,
            status = 'normal'
            )
        except cls.DoesNotExist:
            return None


    class Meta:
        db_table = "member"
        permissions = ()


class RecvAddr(models.Model):
    '''
    用户收货地址表
    '''
    recv_addr_id = models.AutoField(db_column="recv_addr_id", verbose_name="用户收获地址ID", primary_key=True)
    address = models.CharField(db_column="address", verbose_name="街区", max_length=255, null=True, blank=True)
    area_code = models .CharField(db_column="area_code", verbose_name="区号", max_length=255, null=True, blank=True)
    telephone = models.CharField(db_column="telephone", verbose_name="收货地址手机号码", max_length=255, null=True, blank=True)
    username = models.CharField(db_column="username", verbose_name="收件人姓名", max_length=255, null=True, blank=True)
    is_default = models.BooleanField(db_column="is_default", verbose_name="是否默认收货地址", default=False)
    member_id = models.BigIntegerField(db_column="member_id", verbose_name="用户ID")
    status = models.CharField(db_column="status", verbose_name="状态", default="normal", max_length=255)
    

    @classmethod
    def get_recv_addr_data_list(cls, current_page, search_value=None):
        if search_value:
            data_list = cls.objects.filter(**search_value, status='normal'). \
                values(
                    'member_id',
                ).annotate(
                    c = Count('member_id'),
                    ).order_by('-pk')
        else:
            data_list = cls.objects.filter(status='normal'). \
                values(
                    'member_id',
                ).annotate(
                    c = Count('member_id'),
                    ).order_by('-pk')
        p = Paginator(data_list, 15)
        data_list = p.page(current_page).object_list
        for i in data_list:
            i['member_name'] =  Member.get_member_by_id(i['member_id']).member_name
        return data_list
    
    @classmethod
    def get_recv_addr_count(cls, search_value=None):
        if search_value:
            data_count = cls.objects.filter(**search_value, status='normal'). \
                values(
                    'member_id',
                ).annotate(
                    c = Count('member_id'),
                    ).count()
        else:
            data_count = cls.objects.filter(status='normal'). \
                values(
                    'member_id',
                ).annotate(
                    c = Count('member_id'),
                    ).count()
        return data_count
    
    @classmethod
    def get_recv_addr_by_member_id(cls, member_id):
        data_list = cls.objects.filter(
            member_id=member_id,
            status='normal'
        ).values(
            'recv_addr_id', 'address', 'area_code',
            'telephone', 'username',
            'is_default'
        )
        data_list = list(data_list)
        return data_list
    
    
    @classmethod
    def set_is_default(cls, member_id, recv_addr_id, is_default):
        cls.objects.filter(member_id=member_id, status='normal').update(is_default=False)
        cls.objects.filter(member_id=member_id, pk=recv_addr_id).update(is_default=is_default)


    class Meta:
        db_table = 'recv_addr'


class UserOrder(models.Model):
    '''
    用户订单表
    '''
    user_order_id           = models.AutoField(db_column="user_order_id", verbose_name="用户订单表ID", primary_key=True)
    order_num               = models.CharField(db_column="order_num", verbose_name="订单号", null=True, blank=True, max_length=255)
    item_id                 = models.BigIntegerField(db_column="item_id", verbose_name="商品ID", null=True, blank=True)
    item_name               = models.CharField(db_column="item_name", verbose_name="商品名", max_length=255, null=True, blank=True)
    item_count              = models.IntegerField(db_column="item_count", verbose_name="购买数量")
    price                   = models.FloatField(db_column="price", verbose_name="商品单价")
    status_choices = (
        ('new', '等待支付订单'),
        ('paid', '等待发货'),
        ('shipped', '等待收货'),
        ('received', '确认收货'),
        ('close', '订单关闭'),
    )
    order_status            = models.CharField(db_column="order_status", verbose_name="订单状态", choices=status_choices, default="new", max_length=255)
    member_id               = models.BigIntegerField(db_column="member_id", verbose_name="用户ID")
    is_shopping_cart        = models.BooleanField(db_column="is_shupping_cart", verbose_name="是否来自购物车", default=False)
    is_comment              = models.BooleanField(db_column="is_comment", verbose_name="是否评价", default=False)
    recv_addr_id            = models.BigIntegerField(db_column="recv_addr", verbose_name="到货地址ID", null=True, blank=True)
    member_message          = models.CharField(db_column="member_message", verbose_name="用户留言", max_length=1000, null=True, blank=True)
    create_time             = models.IntegerField(db_column="create_time", verbose_name="创建时间", default=int(time.time()))
    pay_time                = models.IntegerField(db_column="pay_time", verbose_name="支付时间", null=True, blank=True)
    status                  = models.CharField(db_column="status", verbose_name="状态", default="normal", max_length=255)


    @classmethod
    def delete_user_order(cls, order_num_list):
        cls.objects.filter(order_num__in=order_num_list).update(status='deleted')
    
    @classmethod
    def update_user_order_by_order_num(cls, order_num, data):
        cls.objects.filter(order_num=order_num).update(**data)

    @classmethod
    def get_user_order_by_member_id(cls, member_id, current_page, order_status):
        order_num_list = cls.objects.filter(member_id=member_id, status='normal'). \
            values('order_num').annotate(c = Count('order_num')).order_by('-pk')
        p = Paginator(order_num_list, 10)
        if int(current_page) > p.num_pages:
            return list()
        order_num_list = p.page(current_page).object_list
        data_list = list()
        for i in order_num_list:
            order_num = i['order_num']
            if order_status:
                obj = cls.objects.filter(
                    order_num=order_num,
                    order_status=order_status,
                    status = "normal"
                ).values()
            else:
                obj = cls.objects.filter(order_num=order_num, status = "normal").values()
            if obj:
                recv_addr = get_model_dict_by_pk(
                        RecvAddr,
                        obj.first()['recv_addr_id']
                )
                data_dict = {
                    'order_num': i['order_num'],
                    'recv_addr': recv_addr,
                    'member_message': obj.first()['member_message'],
                    'all_price': 0,
                    'create_time': common.parse_timestamps(obj.first()['create_time']),
                    'order_status': dict(cls.status_choices)[obj.first()['order_status']],
                    'goods': list()
                }
                for j in obj:
                    item = item_models.Items.get_item_by_id(j['item_id'])
                    image_path = common.build_photo_url(item.photo_id, cdn=True)
                    data_dict['goods'].append({
                        'image_path': image_path,
                        'item_name': j['item_name'],
                        'item_count': j['item_count'],
                        'item_id': j['item_id'],
                        'price': j['price'],
                    })
                    data_dict['all_price'] += float(j['price']) * int(j['item_count'])
                data_list.append(data_dict)
            else:
                return list()
        return data_list

    @classmethod
    def get_user_order_list(cls, current_page, search_value=None):
        data_list =  get_data_list(cls, current_page, search_value=search_value)
        data_list = data_list.values('order_num').annotate(c = Count('order_num'))
        my_list = list()
        for i in data_list:
            order_num = i['order_num']
            obj = cls.objects.filter(order_num=order_num, status = "normal").values()
            if obj:
                recv_addr = get_model_dict_by_pk(
                        RecvAddr,
                        obj.first()['recv_addr_id']
                )
                data_dict = {
                    'member_id': obj.first()['member_id'],
                    'order_num': i['order_num'],
                    'recv_addr': recv_addr,
                    'member_message': obj.first()['member_message'],
                    'all_price': 0,
                    'create_time': common.parse_timestamps(obj.first()['create_time']),
                    'order_status': dict(cls.status_choices)[obj.first()['order_status']],
                    'goods': list()
                }
                for j in obj:
                    item = item_models.Items.get_item_by_id(j['item_id'])
                    photo_id = item.photo_id if item else None
                    image_path = common.build_photo_url(photo_id, cdn=True)
                    data_dict['goods'].append({
                        'image_path': image_path,
                        'item_name': j['item_name'],
                        'item_count': j['item_count'],
                        'price': j['price'],
                    })
                    data_dict['all_price'] += float(j['price']) * int(j['item_count'])
                my_list.append(data_dict)
            else:
                return list()
        return my_list
        


    @classmethod
    def get_user_order_by_order_num(cls, order_num, order_status=None):
        if order_status is not None:
            obj = cls.objects.filter(
                order_num=order_num,
                order_status=order_status,
                status = "normal"
            ).values()
        else:
            obj = cls.objects.filter(order_num=order_num, status = "normal").values()
        recv_addr = get_model_dict_by_pk(
                RecvAddr,
                obj[0]['recv_addr_id']
        )
        data_dict = {
            'order_num': order_num,
            'member_message': obj.first()['member_message'],
            'create_time': common.parse_timestamps(obj.first()['create_time']),
            'order_status': dict(cls.status_choices)[obj.first()['order_status']],
            'recv_addr': recv_addr,
            'goods': list()
        }
        data_dict['all_price'] = 0
        for i in obj:
            item = item_models.Items.get_item_by_id(i['item_id'])
            if item:
                image_path = common.build_photo_url(item.photo_id, cdn=True)
                data_dict['goods'].append({
                    'image_path': image_path,
                    'item_name': i['item_name'],
                    'item_count': i['item_count'],
                    'item_id': i['item_id'],
                    'price': i['price'],
                    'order_status': dict(cls.status_choices)[i['order_status']],
                })
                data_dict['all_price'] += float(i['price']) * int(i['item_count'])
            else:
                data_dict['goods'].append({
                    'item_name': i['item_name'] + '（商品已经下架）',
                    'item_count': i['item_count'],
                    'price': i['price'],
                    'order_status': dict(cls.status_choices)[i['order_status']],
                })
                data_dict['all_price'] += float(i['price']) * int(i['item_count'])
        return data_dict
    
    @classmethod
    def get_user_order_data_list(cls, current_page, search_value=None):
        if search_value:
            data_list = cls.objects.filter(**search_value, status='normal'). \
                values(
                    'order_num', 'order_status', 'member_id',
                    'create_time'
                ).annotate(
                    c = Count('order_num'),
                    ).order_by('-pk')
        else:
            data_list = cls.objects.filter(status='normal'). \
                values(
                    'order_num', 'order_status', 'member_id',
                    'create_time'
                ).annotate(
                    c = Count('order_num'),
                    ).order_by('-pk')
        p = Paginator(data_list, 15)
        return p.page(current_page).object_list
    
    @classmethod
    def get_user_order_count(cls, search_value=None):
        if search_value:
            data_count = cls.objects.filter(**search_value, status='normal'). \
                values(
                    'order_num', 'order_status', 'member_id',
                    'create_time'
                ).annotate(
                    c = Count('order_num'),
                    ).count()
        else:
            data_count = cls.objects.filter(status='normal'). \
                values(
                    'order_num', 'order_status', 'member_id',
                    'create_time'
                ).annotate(
                    c = Count('order_num'),
                    ).count()
        return data_count
    
    @classmethod
    def has_order_num(cls, order_num):
        obj = cls.objects.filter(order_num=order_num).first()
        return True if obj else False
    
    @classmethod
    def get_user_order_obj_by_order_num(cls, order_num):
        return cls.objects.filter(order_num=order_num).first()
    
    @classmethod
    def get_user_order_all_status_count(cls, member_id):
        order_status_help = {
            'new': '待支付',
            'paid': '待发货',
            'shipped': '待收货',
        }
        data_list = list()
        data = cls.objects.filter(member_id=member_id, status='normal'). \
            values_list('order_status').annotate(c=Count('order_status'))
        data = dict(data)
        for i in order_status_help:
            data_list.append({
                order_status_help[i]: data.get(i) if data.get(i) is not None else 0
            })
        data_list.append({
            '待评价': cls.objects.filter(
                         member_id=member_id,
                         status='normal',
                         is_comment=False,
                         order_status='received'
                     ).count()
        })
        return data_list


    class Meta:
        db_table = "user_order"


class UserCollectionItem(models.Model):
    user_collection_id = models.AutoField(db_column="user_collection_id", verbose_name="用户收藏商品id", primary_key=True)
    member_id = models.BigIntegerField(db_column="member_id", verbose_name="用户ID")
    item_id = models.BigIntegerField(db_column="item_id", verbose_name="商品ID", null=True, blank=True)
    create_time = models.IntegerField(db_column="create_time", verbose_name="创建时间", default=int(time.time()))
    status = models.CharField(db_column="status", verbose_name="状态", default="normal", max_length=255)


    @classmethod
    def user_has_collection_item(cls, member_id, item_id):
        return True if cls.objects.filter(member_id=member_id, item_id=item_id, status='normal') else False

    @classmethod
    def get_user_collection_item(cls, member_id):
        objs = cls.objects.filter(member_id=member_id, status='normal').values_list('item_id').order_by('-pk')
        if objs:
            item_id_list = [i[0] for i in objs]
            return item_id_list
        else:
            return list()
    

    class Meta:
        db_table = 'user_collection_item'


class OutOrder(models.Model):
    out_order_id = models.AutoField(db_column="out_order_id", verbose_name="外部订单表ID", primary_key=True)
    member_nickname = models.CharField(db_column='member_nickname', verbose_name='用户昵称', max_length=255, null=True, blank=True)
    wechat_id = models.CharField(db_column='wechat_id', verbose_name='微信号', max_length=255, null=True, blank=True)
    wechat_nickname = models.CharField(db_column='wechat_nickname', verbose_name='微信昵称', max_length=2555, null=True, blank=True)
    source = models.CharField(db_column='source', verbose_name='发货地', max_length=255, null=True, blank=True)
    order_id = models.CharField(db_column='order_id', verbose_name='订单ID', max_length=255, null=True, blank=True)
    place_date = models.IntegerField(db_column='place_date', verbose_name='地方时间', null=True, blank=True)
    placed_at = models.CharField(db_column='placed_at', verbose_name='地方标准时间', max_length=255, null=True, blank=True)
    member_level = models.CharField(db_column='member_level', verbose_name='会员等级', max_length=255, null=True, blank=True)
    order_status = models.CharField(db_column='order_status', verbose_name='订单状态', max_length=255, null=True, blank=True)
    member_phone = models.CharField(db_column='member_phone', verbose_name='手机号', max_length=255, null=True, blank=True)
    status = models.CharField(db_column="status", verbose_name="状态", default="normal", max_length=255)

    @classmethod
    def default_table_head(cls):
        head = {
            'order_id': '订单ID',
            'member_nickname': '用户昵称',
            'wechat_id': '微信号',
            'wechat_nickname': '微信昵称',
            'order_id': '发货地',
            'placed_at': '地方时间',
            'member_level': '会员等级',
            'order_status': '订单状态',
            'member_phone': '手机号',
        }
        return head

    @classmethod
    def list_out_order(cls):
        # conds = {
        #     "status": "normal",
        #     # "order_status": {"$in": export_weike_orders},
        #     "source": {"$regex": u"微客"},
        #     "order_status": {"$regex": u"(交易完成|已发货)"},
        #     "$and": [{"place_date": {"$lte": 20180531}}, {"place_date": {"$gte": 20180501}}]
        # }
        data_list = cls.objects.filter(
            (Q(order_status__icontains='交易完成') | Q(order_status__icontains='已发货')), 
            status="normal",
            source__icontains='微客',
            place_date__range=[20180501, 20180531]
        ).values("order_id", "member_nickname", "source", "member_level", "placed_at")
        for i in data_list:
            i['member_nickname'] = eval(i['member_nickname']).decode()
        return data_list


    class Meta:
        db_table = "out_order"


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

def get_or_create_model_data(model, data):
    return model.objects.get_or_create(**data)

def update_or_create_model_data(model, data):
    return model.objects.update_or_create(**data)

def update_model_data_by_pk(model, pk, data):
    model.objects.filter(pk=pk).update(**data)

def get_model_dict_by_pk(model, pk):
    obj = model.objects.filter(pk=pk).first()
    obj = model_to_dict(obj) if obj else None
    return obj

