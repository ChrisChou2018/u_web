from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.db.models import Q

from my_admin import member_models
from my_admin import item_models
from my_admin import models


def my_render(request, templater_path, **kwargs):
    return render(request, templater_path, dict(**kwargs))

def member_signin(request):
    if request.method == "GET":
        return my_render(
            request,
            'admin/a_signin.html',
        )
    else:
        telephone = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(telephone=telephone, password=password)
        if user and user.is_admin:
            login(request, user)
            return redirect('/myadmin/index/')
        else:
            return my_render(
                request,
                'admin/a_signin.html',
                form_error = '用户名或者密码错误',
                form_data = request.POST
            )

def member_signout(request):
    logout(request)
    return redirect('/myadmin/signin/')

@login_required(login_url='/myadmin/signin/')
def index(request):
    if request.method == "GET":
        return render(
            request,
            'admin/a_index.html'
        )


class UserChangeForm(forms.ModelForm):

    password2 = forms.CharField(error_messages={'required': '新密码不能为空'})

    class Meta:
        model = member_models.Member
        fields = set()

    def clean_password(self):
        password = self.cleaned_data["password2"]
        return password

    def update_pass(self):
        user = super(UserChangeForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password2"])
        user.save()


@login_required(login_url='/myadmin/signin/')
def change_pass(request):
    if request.method == 'GET':
        return my_render(
            request,
            'admin/a_change_password.html',
        )
    else:
        password = request.POST.get('password')
        telephone = request.user.telephone
        user = authenticate(telephone=telephone, password=password)
        if not user:
            return my_render(
                request,
                'admin/a_change_password.html',
                form_error = '原密码错误',
                form_data = request.POST
            )
        form = UserChangeForm(request.POST)
        if not form.is_valid():
            return my_render(
                request,
                'admin/a_change_password.html',
                form_error = form.errors.get('password2'),
                form_data = request.POST
            )
        form.update_pass()
        return redirect('/myadmin/signin/')

def member_manage(request):
    if request.method == "GET":
        GET = request.GET.get
        current_page = GET('page', 1)
        value = GET('search_value', '')
        filter_args = None
        if value:
            filter_args = '&search_value={0}'.format(value)
            search_value = (
                Q(member_name = value) | \
                Q(telephone = value)
            )
            member_list = member_models.Member. \
                get_member_list(current_page, search_value)
            member_count = member_models.Member. \
                get_member_count(search_value)
        else:
            member_list = member_models.Member. \
            get_member_list(current_page)
            member_count = member_models.Member.get_member_count()
        uri = request.path
        table_head = member_models.Member.get_style_table_head()
        return my_render(
            request,
            'admin/a_member_manage.html',
            current_page = current_page,
            member_list = member_list,
            member_count = member_count,
            uri = uri,
            filter_args = filter_args,
            table_head = table_head,
            search_value = value
        )

def items_manage(request):
    if request.method == 'GET':
        current_page = request.GET.get('page', 1)
        value = request.GET.get('search_value', '')
        filter_args = None
        if value:
            filter_args = '&search_value={0}'.format(value)
            search_value = {"item_name" : value}
            item_list = item_models.Items.get_list_items(current_page, search_value)
            item_count = item_models.Items.get_items_count(search_value)
        else:
            item_list = item_models.Items.get_list_items(current_page)
            item_count = item_models.Items.get_items_count()
        uri = request.path
        specifications_type_dict = dict(item_models.Items. \
            specifications_type_choices)
        brand_dict = item_models.Brands.get_brands_dict_for_all()
        categories_dict = item_models.Categories.get_categoreis_dict_for_all()
        return my_render(
            request,
            'admin/a_items_manage.html',
            current_page = current_page,
            filter_args = filter_args,
            item_list = item_list,
            item_count = item_count,
            uri = uri,
            specifications_type_dict = specifications_type_dict,
            brand_dict = brand_dict,
            categories_dict = categories_dict,
        )


class AddItemForm(forms.ModelForm):
    item_name = forms.CharField(error_messages={'required': '至少这个不可以为空'})

    class Meta:
        model = item_models.Items
        fields = (
            "item_name", "item_info", "item_code",
            "item_barcode", "price", "current_price",
            "foreign_price", "key_word", "origin",
            "shelf_life", "capacity", "specifications_type_id",
            "for_people", "weight", "brand_id",
            "categories_id"
        )
    def save(self, commit=True, request=None):
        item = super(AddItemForm, self).save(commit=False)
        if commit:
            item.create_person = request.user.member_name
            item.save()
        return item


def add_item(request):
    specifications_type_dict = dict(
        item_models.Items.specifications_type_choices
    )
    brands_dict = item_models.Brands.get_brands_dict_for_all()
    categories_dict = item_models.Categories.get_categoreis_dict_for_all()
    if request.method == 'GET':
        return my_render(
            request,
            'admin/a_add_item.html',
            specifications_type_dict = specifications_type_dict,
            brands_dict = brands_dict,
            categories_dict = categories_dict,
        )
    else:
        form = AddItemForm(request.POST)
        if not form.is_valid():
            return my_render(
                request,
                'admin/a_add_item.html',
                specifications_type_dict = specifications_type_dict,
                brands_dict = brands_dict,
                categories_dict = categories_dict,
                form_errors = form.errors,
            )
        form.save(request=request)
        return redirect('/myadmin/item_manage/')

def editor_item(request):
    pass