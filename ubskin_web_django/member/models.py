import time

from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser, PermissionsMixin
)
from django.forms.models import model_to_dict
from django.core.paginator import Paginator


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
