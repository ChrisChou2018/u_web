import time

from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser, PermissionsMixin
)
from django.forms.models import model_to_dict
from django.core.paginator import Paginator
from django.db.models import Count


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
    # role                = models.CharField(db_column="role", default="")

    objects = UserProfileManager()
    USERNAME_FIELD = 'user_name'
    REQUIRED_FIELDS = ['member_name']

    def __str__(self):  # __unicode__ on Python 2
        return self.member_name
    
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
    addr_name = models.CharField(db_column="addr_name", verbose_name="收货地址", max_length=255)
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
                    )
        else:
            data_list = cls.objects.filter(status='normal'). \
                values(
                    'member_id',
                ).annotate(
                    c = Count('member_id'),
                    )
        p = Paginator(data_list, 15)
        return p.page(current_page).object_list
    
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
        ).values('recv_addr_id', 'addr_name')
        data_list = list(data_list)
        return data_list


    class Meta:
        db_table = 'recv_addr'


class UserOrder(models.Model):
    '''
    用户订单表
    '''
    user_order_id           = models.AutoField(db_column="user_order_id", verbose_name="用户订单表ID", primary_key=True)
    order_num               = models.CharField(db_column="order_num", verbose_name="订单号", null=True, blank=True, max_length=255)
    item_id                 = models.BigIntegerField(db_column="item_id", verbose_name="商品ID", null=True, blank=True)
    item_name               = models.CharField(db_column="item_name", verbose_name="支付状态", max_length=255, null=True, blank=True)
    item_count              = models.IntegerField(db_column="item_count", verbose_name="购买数量")
    price                   = models.FloatField(db_column="price", verbose_name="商品单价")
    status_choices = (
        ('new', '等待支付订单'),
        ('paid', '等待发货（已经支付）'),
        ('shipped', '等待收获（已经支付）'),
        ('received', '确认收获（已经支付）'),
    )
    order_status            = models.CharField(db_column="order_status", verbose_name="订单状态", choices=status_choices, default="new", max_length=255)
    member_id               = models.BigIntegerField(db_column="member_id", verbose_name="用户ID")
    recv_addr               = models.CharField(db_column="recv_addr", verbose_name="到货地址", max_length=255, null=True, blank=True)
    create_time             = models.IntegerField(db_column="create_time", verbose_name="创建时间", default=int(time.time()))
    status                  = models.CharField(db_column="status", verbose_name="状态", default="normal", max_length=255)


    @classmethod
    def get_user_order_by_member_id(cls, member_id):
        return cls.objects.filter(member_id=member_id, status='normal').values()
    
    @classmethod
    def get_user_order_data_list(cls, current_page, search_value=None):
        if search_value:
            data_list = cls.objects.filter(**search_value, status='normal'). \
                values(
                    'order_num', 'order_status', 'member_id',
                    'create_time'
                ).annotate(
                    c = Count('order_num'),
                    )
        else:
            data_list = cls.objects.filter(status='normal'). \
                values(
                    'order_num', 'order_status', 'member_id',
                    'create_time'
                ).annotate(
                    c = Count('order_num'),
                    )
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


    class Meta:
        db_table = "user_order"


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

def update_model_data_by_pk(model, pk, data):
    model.objects.filter(pk=pk).update(**data)