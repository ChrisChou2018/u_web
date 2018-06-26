import time

from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser, PermissionsMixin
)
from django.forms.models import model_to_dict
from django.core.paginator import Paginator


class UserProfileManager(BaseUserManager):
    def create_user(self, telephone, member_name, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not telephone:
            raise ValueError('必须要注册手机号码')

        user = self.model(
            telephone=telephone,
            member_name=member_name,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, telephone, member_name, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(telephone,
            password=password,
            member_name=member_name
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class Member(AbstractBaseUser, PermissionsMixin):
    member_id           = models.AutoField(db_column="member_id", primary_key=True, verbose_name="用户ID")
    member_name         = models.CharField(db_column="member_name", max_length=255)
    telephone           = models.CharField(db_column="telephone", max_length=255, unique=True)
    status              = models.CharField(db_column="status", default='normal', max_length=255)
    sessions            = models.CharField(db_column="sessions", max_length=255)
    created_ip          = models.CharField(db_column="created_ip", null=True, max_length=255)
    create_time         = models.IntegerField(db_column="create_time", default=int(time.time()))
    update_time         = models.IntegerField(db_column="update_time", default=int(time.time()))
    is_active           = models.BooleanField(default=True)
    is_admin            = models.BooleanField(default=False)
    is_staff            = models.BooleanField(default=True)
    avatar              = models.CharField(db_column="avatar", max_length=255, null=True, blank=True)
    # role                = models.CharField(db_column="role", default="")

    objects = UserProfileManager()
    USERNAME_FIELD = 'telephone'
    REQUIRED_FIELDS = ['member_name']

    def __str__(self):  # __unicode__ on Python 2
        return self.member_name
    
    def get_full_name(self):
        return self.member_name

    def get_short_name(self):
        return self.member_name

    @classmethod
    def get_member_list(cls, current_page, search_value=None):
        if search_value:
            member_obj = cls.objects.filter(search_value, status='normal'). \
                order_by("-member_id")
        else:
            member_obj = cls.objects.filter(status='normal'). \
                order_by("-member_id")
        p = Paginator(member_obj, 15)
        return p.page(current_page).object_list.values()   
    
    @classmethod
    def get_member_count(cls, search_value=None):
        if search_value:
            member_obj_count = Member.objects.filter(search_value, status='normal').count()
        else:
            member_obj_count = Member.objects.filter(status='normal').count()
        return member_obj_count

    @classmethod
    def get_style_table_head(cls):
        return dict(
            member_id = '用户ID',
            member_name = '用户名',
            telephone = '手机号',
            is_admin = '管理员身份',
            is_staff = '内部账号',
            more = '更多'
        )
    
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


    class Meta:
        db_table = "member"
        permissions = ()

