import os

from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.db.models import Q
from django.forms import model_to_dict
from django.conf import settings

from my_admin import member_models
from my_admin import item_models
from my_admin import models
from ubskin_web_django.common import photo


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
            item_list = item_models.Items. \
                get_list_items(current_page, search_value)
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
            'admin/a_item_manage.html',
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


class EditorItemForm(forms.ModelForm):
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
    def update(self, item_id, request=None):
        item = self._meta.model
        update_person = request.user.member_name
        data = self.cleaned_data
        data.update({'update_person': update_person})
        item.update_item_by_id(item_id, data)
        return item



def editor_item(request):
    specifications_type_dict = dict(
        item_models.Items.specifications_type_choices
    )
    brands_dict = item_models.Brands.get_brands_dict_for_all()
    categories_dict = item_models.Categories.get_categoreis_dict_for_all()
    item_id = request.GET.get('item_id')
    item_obj = item_models.Items.get_item_by_id(item_id)
    form_data = model_to_dict(item_obj)
    back_url = request.GET.get('back_url')
    if request.method == 'GET':
        return my_render(
            request,
            'admin/a_add_item.html',
            form_data = form_data,
            specifications_type_dict = specifications_type_dict,
            brands_dict = brands_dict,
            categories_dict = categories_dict,
        )
    else:
        form = EditorItemForm(request.POST)
        if not form.is_valid():
            return my_render(
                request,
                'admin/a_add_item.html',
                specifications_type_dict = specifications_type_dict,
                brands_dict = brands_dict,
                categories_dict = categories_dict,
                form_errors = form.errors,
            )
        form.update(item_id, request)
        return redirect(back_url)
        


def item_image_manage(request):
    if request.method == "GET":
        item_id = request.GET.get('item_id')
        item_image_list = item_models.ItemImages.get_images_by_itemid(item_id)
        item_obj  = item_models.Items.get_item_by_id(item_id)
        image_dict = {}
        for i in item_image_list:
            if i['image_type'] not in image_dict:
                image_dict[i['image_type']] = [
                    {'image_path': i['image_path'], 'image_id': i['image_id']}
                ]
            else:
                image_dict[i['image_type']].append(
                    {'image_path': i['image_path'], 'image_id': i['image_id']}
                )
        return my_render(
            request,
            'admin/a_item_image_manage.html',
            image_dict = image_dict,
            item_obj = item_obj,
        )

def brand_manage(request):
    if request.method == 'GET':
        current_page = request.GET.get('page', 1)
        value = request.GET.get('search_value', '')
        filter_args = None
        if value:
            filter_args = '&search_value={0}'.format(value)
            search_value = {"cn_name": value}
            brands_list = item_models.Brands.get_list_brands(current_page, search_value)
            brands_count = item_models.Brands.get_brands_count(search_value)
        else:
            brands_list = item_models.Brands.get_list_brands(current_page)
            brands_count = item_models.Brands.get_brands_count()
        return my_render(
            request,
            'admin/a_brand_manage.html',
            search_value = value,
            current_page = current_page,
            filter_args = filter_args,
            brands_list = brands_list,
            brands_count = brands_count,
        )


class AddBrandForm(forms.ModelForm):
    cn_name = forms.CharField(error_messages={'required': '至少这个不可以为空'})

    class Meta:
        model = item_models.Brands
        fields = (
            'cn_name', 'cn_name_abridge', 'en_name',
            'form_country', 'key_word', 'brand_about'
        )


    def save(self, commit=True, request=None):
        item = super(AddBrandForm, self).save(commit=False)
        if commit:
            item.save()
        return item


def add_brand(request):
    if request.method == 'GET':
        return my_render(
            request,
            'admin/a_add_brand.html',
        )
    else:
        form = AddBrandForm(request.POST)
        if not form.is_valid():
            return my_render(
                request,
                'admin/a_add_brand.html',
                form_errors = form.errors,
            )
        brand = form.save()
        files = request.FILES
        if files:
            file_obj = files.get('brand_image')
            server_file_path = '/media/photos'
            file_dir = os.path.join(
                settings.MEDIA_ROOT,
                'photos'
            )
            if not os.path.exists(file_dir):
                os.makedirs(file_dir)
            data = photo.save_upload_photo(
                file_obj,
                file_dir,
                server_file_path,
                'brand'
            )
            if data:
                brand.brand_image = data['image_path']
                brand.save()
        return redirect('/myadmin/brand_manage/')


class EditorBrandForm(forms.ModelForm):
    cn_name = forms.CharField(error_messages={'required': '至少这个不可以为空'})

    class Meta:
        model = item_models.Brands
        fields = (
            'cn_name', 'cn_name_abridge', 'en_name',
            'form_country', 'key_word', 'brand_about'
        )


    def update(self, brand_id):
        item = self._meta.model
        data = self.cleaned_data
        item.update_brand_by_id(brand_id, data)
        return item


def editor_brand(request):
    brand_id = request.GET.get('brand_id')
    if request.method == 'GET':
        item_obj = item_models.Brands.get_brand_by_id(brand_id)
        form_data = model_to_dict(item_obj)
        return my_render(
            request,
            'admin/a_add_brand.html',
            form_data = form_data,
        )
    else:
        form = EditorBrandForm(request.POST)
        item_obj = item_models.Brands.get_brand_by_id(brand_id)
        if not form.is_valid():
            return my_render(
                request,
                'admin/a_add_brand.html',
                form_errors = form.errors,
            )
        form.update(brand_id)
        files = request.FILES
        if files:
            file_obj = files.get('brand_image')
            server_file_path = '/media/photos'
            file_dir = os.path.join(
                settings.MEDIA_ROOT,
                'photos'
            )
            if not os.path.exists(file_dir):
                os.makedirs(file_dir)
            data = photo.save_upload_photo(
                file_obj,
                file_dir,
                server_file_path,
                'brand'
            )
            if data:
                item_obj.brand_image = data['image_path']
                item_obj.save()
        back_url = request.GET.get('back_url')
        return redirect(back_url)

def categorie_manage(request):
    if request.method == 'GET':
        current_page = request.GET.get('page', 1)
        value = request.GET.get('search_value', '')
        filter_args = None
        categorie_choices = dict(item_models.Categories.type_choices)
        if value:
            filter_args = '&search_value={0}'.format(value)
            search_value = {'categorie_name': value}
            categories_list = item_models.Categories. \
                get_list_categories(current_page, search_value)
            categories_count = item_models.Categories. \
                get_categories_count(search_value)
        else:
            categories_list = item_models.Categories. \
                get_list_categories(current_page)
            categories_count = item_models.Categories. \
                get_categories_count()

        return my_render(
            request,
            'admin/a_categorie_manage.html',
            current_page = current_page,
            search_value = value,
            filter_args = filter_args,
            categorie_choices = categorie_choices,
            categories_list = categories_list,
            categories_count = categories_count,
        )


class AddCategorieForm(forms.ModelForm):
    categorie_name = forms.CharField(error_messages={'required': '不可以为空'})
    categorie_type = forms.IntegerField(error_messages={'required': '请选择一个所属分类'})

    class Meta:
        model = item_models.Categories
        fields = (
            'categorie_name', 'categorie_type',
        )


    def save(self, commit=True, request=None):
        categorie = super(AddCategorieForm, self).save(commit=False)
        if commit:
            categorie.save()
        return categorie


def add_categorie(request):
    categorie_choices = dict(item_models.Categories.type_choices)
    if request.method == 'GET':
        return my_render(
            request,
            'admin/a_add_categorie.html',
            categorie_choices = categorie_choices,
        )
    else:
        form = AddCategorieForm(request.POST)
        if not form.is_valid():
            return my_render(
                request,
                'admin/a_add_categorie.html',
                form_errors = form.errors,
                categorie_choices = categorie_choices,
            )
        categorie = form.save()
        files = request.FILES
        if files:
            file_obj = files.get('categorie_image')
            server_file_path = '/media/photos'
            file_dir = os.path.join(
                settings.MEDIA_ROOT,
                'photos'
            )
            if not os.path.exists(file_dir):
                os.makedirs(file_dir)
            data = photo.save_upload_photo(
                file_obj,
                file_dir,
                server_file_path,
                'brand'
            )
            if data:
                categorie.image_path = data['image_path']
                categorie.save()
        return redirect('/myadmin/categorie_manage/')


class EditorCategorieForm(forms.ModelForm):
    categorie_name = forms.CharField(error_messages={'required': '不可以为空'})
    categorie_type = forms.IntegerField(error_messages={'required': '请选择一个所属分类'})

    class Meta:
        model = item_models.Categories
        fields = (
            'categorie_name', 'categorie_type',
        )


    def update(self, categorie_id):
        categorie = self._meta.model
        data = self.cleaned_data
        categorie.update_categorie_by_id(categorie_id, data)


def editor_categorie(request):
    categorie_id = request.GET.get('categorie_id')
    categorie = item_models.Categories.get_categorie_by_id(categorie_id)
    form_data = model_to_dict(categorie)
    categorie_choices = dict(item_models.Categories.type_choices)
    if request.method == 'GET':
        return my_render(
            request,
            'admin/a_add_categorie.html',
            form_data = form_data,
            categorie_choices = categorie_choices,
        )
    else:
        form = EditorCategorieForm(request.POST)
        if not form.is_valid():
            return my_render(
                request,
                'admin/a_add_categorie.html',
                form_errors = form.errors,
                categorie_choices = categorie_choices,
            )
        form.update(categorie_id)
        files = request.FILES
        if files:
            file_obj = files.get('categorie_image')
            server_file_path = '/media/photos'
            file_dir = os.path.join(
                settings.MEDIA_ROOT,
                'photos'
            )
            if not os.path.exists(file_dir):
                os.makedirs(file_dir)
            data = photo.save_upload_photo(
                file_obj,
                file_dir,
                server_file_path,
                'brand'
            )
            if data:
                categorie.image_path = data['image_path']
                categorie.save()
        back_url = request.GET.get('back_url')
        return redirect(back_url)

def item_comment_manage(request):
    if request.method == 'GET':
        current_page = request.GET.get('page', 1)
        value = request.GET.get('search_value', '')
        filter_args = None
        if value:
            filter_args = '&search_value={0}'.format(value)
            item_id = item_models.Items.get_item_id_by_item_name(value)
            if item_id:
                search_value = {'item_id': item_id}
            item_comments_list = item_models.ItemComments. \
                get_item_comments_list(current_page, search_value)
            count = item_models.ItemComments. \
                get_item_comments_count(search_value)
        else:
            item_comments_list = item_models.ItemComments. \
                get_item_comments_list(current_page)
            count = item_models.ItemComments.get_item_comments_count()
        return my_render(
            request,
            'admin/a_item_comment_manage.html',
            current_page = current_page,
            search_value = value,
            filter_args = filter_args,
            item_comments_list = item_comments_list,
            count = count,
        )

def item_comment_image_manage(request):
    if request.method == 'GET':
        comment_id = request.GET.get('comment_id')
        comment_image_list = item_models.CommentImages.get_comment_image_obj_by_id(comment_id)
        return my_render(
            request,
            'admin/a_editor_comment_image.html',
            comment_image_list = comment_image_list,
        )


class EditorItemCommentForm(forms.ModelForm):

    class Meta:
        model = item_models.ItemComments
        fields = (
            'comment_content',
        )


    def update(self, comment_id):
        categorie = self._meta.model
        data = self.cleaned_data
        categorie.update_item_comment_by_id(comment_id, data)


def edit_item_comment(request):
    comment_id = request.GET.get('comment_id')
    form_data = item_models.ItemComments.get_item_comment_by_id(comment_id)
    if request.method == 'GET':
        return my_render(
            request,
            'admin/a_editor_comment.html',
            form_data = form_data,
        )
    else:
        form = EditorItemCommentForm(request.POST)
        if not form.is_valid():
            return my_render(
                request,
                'admin/a_editor_comment.html',
                form_data = form_data,
            )
        form.update(comment_id)
        back_url = request.GET.get('back_url')
        return redirect(back_url)

    