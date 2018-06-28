import os

from django.shortcuts import render
from django.http import HttpResponseRedirect as redirect
from django import forms
from django.forms import model_to_dict
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Count

from ubskin_web_django.item import models as item_models
from ubskin_web_django.common import photo
from ubskin_web_django.common import common


def my_render(request, templater_path, **kwargs):
    return render(request, templater_path, dict(**kwargs))

@login_required(login_url='/myadmin/signin/')
def items_manage(request):
    if request.method == 'GET':
        current_page = request.GET.get('page', 1)
        value = request.GET.get('search_value', '')
        filter_args = None
        if value:
            filter_args = '&search_value={0}'.format(value)
            search_value = {"item_name" : value}
            item_list = item_models.get_data_list(
                item_models.Items,
                current_page,
                search_value
            )
            item_count = item_models.get_data_count(
                item_models.Items,
                search_value
            )
        else:
            item_list = item_models.get_data_list(
                item_models.Items,
                current_page
            )
            item_count = item_models.get_data_count(
                item_models.Items
            )
        uri = request.path
        specifications_type_dict = dict(item_models.Items. \
            specifications_type_choices)
        brand_dict = item_models.Brands.get_brands_dict_for_all()
        categories_dict = item_models.Categories.get_categoreis_dict_for_all()
        return my_render(
            request,
            'item/a_item_manage.html',
            current_page = current_page,
            filter_args = filter_args,
            item_list = item_list,
            item_count = item_count,
            uri = uri,
            specifications_type_dict = specifications_type_dict,
            brand_dict = brand_dict,
            categories_dict = categories_dict,
            search_value = value,
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

@login_required(login_url='/myadmin/signin/')
def add_item(request):
    specifications_type_dict = dict(
        item_models.Items.specifications_type_choices
    )
    brands_dict = item_models.Brands.get_brands_dict_for_all()
    categories_dict = item_models.Categories.get_categoreis_dict_for_all()
    if request.method == 'GET':
        return my_render(
            request,
            'item/a_add_item.html',
            specifications_type_dict = specifications_type_dict,
            brands_dict = brands_dict,
            categories_dict = categories_dict,
        )
    else:
        form = AddItemForm(request.POST)
        if not form.is_valid():
            return my_render(
                request,
                'item/a_add_item.html',
                specifications_type_dict = specifications_type_dict,
                brands_dict = brands_dict,
                categories_dict = categories_dict,
                form_errors = form.errors,
                form_data = request.POST,
            )
        form.save(request=request)
        return redirect('/myadmin/item_manage/')


class EditorItemForm(forms.Form):
    item_id = forms.IntegerField()
    item_name = forms.CharField(error_messages={'required': '至少这个不可以为空'})
    item_info = forms.CharField(required=False)
    item_code = forms.CharField(required=False)
    item_barcode = forms.CharField(required=False)
    price = forms.FloatField(required=False)
    current_price = forms.FloatField(required=False)
    foreign_price = forms.FloatField(required=False)
    key_word = forms.CharField(required=False)
    origin = forms.CharField(required=False)
    shelf_life = forms.CharField(required=False)
    capacity = forms.CharField(required=False)
    specifications_type_id = forms.IntegerField(required=False)
    for_people = forms.CharField(required=False)
    weight = forms.IntegerField(required=False)
    brand_id = forms.IntegerField(required=False)
    categories_id = forms.IntegerField(required=False)


    def clean_item_code(self):
        item_code = self.cleaned_data['item_code']
        item_id = self.cleaned_data['item_id']
        if item_models.Items.has_exist_item_code(item_code, item_id):
            raise forms.ValidationError("当前商品编码已经存在")
        return item_code
    
    def clean_item_barcode(self):
        item_barcode = self.cleaned_data['item_barcode']
        item_id = self.cleaned_data['item_id']
        if item_models.Items.has_exist_item_barcode(item_barcode, item_id):
            raise forms.ValidationError("当前商品条码已经存在")
        return item_barcode

    def update(self, item_id, request=None):
        item = item_models.Items
        update_person = request.user.member_name
        data = self.cleaned_data
        item_id = data.pop('item_id')
        data.update({'update_person': update_person})
        item.update_item_by_id(item_id, data)
        return item


@login_required(login_url='/myadmin/signin/')
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
            'item/a_add_item.html',
            form_data = form_data,
            specifications_type_dict = specifications_type_dict,
            brands_dict = brands_dict,
            categories_dict = categories_dict,
        )
    else:
        form = EditorItemForm(request.POST)
        if not form.is_valid():
            print(form.errors)
            return my_render(
                request,
                'item/a_add_item.html',
                form_data = form_data,
                specifications_type_dict = specifications_type_dict,
                brands_dict = brands_dict,
                categories_dict = categories_dict,
                form_errors = form.errors,
            )
        form.update(item_id, request)
        return redirect(back_url)

@login_required(login_url='/myadmin/signin/')  
def item_image_manage(request):
    if request.method == "GET":
        item_id = request.GET.get('item_id')
        item_image_list = item_models.ItemImages.get_item_images_by_itemid(item_id)
        item_info_image_list = item_models.ItemImages.get_item_info_images_by_itemid(item_id)
        item_obj  = item_models.Items.get_item_by_id(item_id)
        item_image_dict = {}
        for i in item_image_list:
            if "title" not in item_image_dict:
                item_image_dict['title'] = [{
                    'image_path': common.build_photo_url(i['photo_id'], pic_version='title'),
                    'image_id': i['image_id']
                }]
            else:
                item_image_dict["title"].append({
                    'image_path': common.build_photo_url(i['photo_id'], pic_version='title'),
                    'image_id': i['image_id']
                })
        for i in item_info_image_list:
            if "item" not in item_image_dict:
                item_image_dict['item'] = [{
                    'image_path': common.build_photo_url(i['photo_id'], pic_version='item'),
                    'image_id': i['image_id']
                }]
            else:
                item_image_dict["item"].append({
                    'image_path': common.build_photo_url(i['photo_id'], pic_version='item'),
                    'image_id': i['image_id']
                })
        return my_render(
            request,
            'item/a_item_image_manage.html',
            item_image_dict = item_image_dict,
            item_obj = item_obj,
        )

@login_required(login_url='/myadmin/signin/')
def brand_manage(request):
    if request.method == 'GET':
        current_page = request.GET.get('page', 1)
        value = request.GET.get('search_value', '')
        filter_args = None
        if value:
            filter_args = '&search_value={0}'.format(value)
            search_value = {"cn_name": value}
            brands_list = item_models.get_data_list(
                item_models.Brands,
                current_page,
                search_value
            )
            brands_count = item_models.get_data_count(
                item_models.Brands,
                search_value
            )
        else:
            brands_list = item_models.get_data_list(
                item_models.Brands,
                current_page,
            )
            brands_count = item_models.get_data_count(
                item_models.Brands
            )
        return my_render(
            request,
            'item/a_brand_manage.html',
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


@login_required(login_url='/myadmin/signin/')
def add_brand(request):
    if request.method == 'GET':
        return my_render(
            request,
            'item/a_add_brand.html',
        )
    else:
        form = AddBrandForm(request.POST)
        if not form.is_valid():
            return my_render(
                request,
                'item/a_add_brand.html',
                form_errors = form.errors,
            )
        brand = form.save()
        files = request.FILES
        if files:
            file_obj = files.get('brand_image')
            if not os.path.exists(settings.MEDIA_ROOT,):
                os.makedirs(settings.MEDIA_ROOT,)
            data = photo.save_upload_photo(
                file_obj,
                settings.MEDIA_ROOT,
            )
            if data:
                brand.photo = data['photo_id']
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


@login_required(login_url='/myadmin/signin/')
def editor_brand(request):
    brand_id = request.GET.get('brand_id')
    if request.method == 'GET':
        item_obj = item_models.Brands.get_brand_by_id(brand_id)
        form_data = model_to_dict(item_obj)
        return my_render(
            request,
            'item/a_add_brand.html',
            form_data = form_data,
        )
    else:
        form = EditorBrandForm(request.POST)
        item_obj = item_models.Brands.get_brand_by_id(brand_id)
        if not form.is_valid():
            return my_render(
                request,
                'item/a_add_brand.html',
                form_errors = form.errors,
            )
        form.update(brand_id)
        files = request.FILES
        if files:
            file_obj = files.get('brand_image')
            if not os.path.exists(settings.MEDIA_ROOT,):
                os.makedirs(settings.MEDIA_ROOT,)
            data = photo.save_upload_photo(
                file_obj,
                settings.MEDIA_ROOT,
            )
            if data:
                item_obj.photo_id = data['photo_id']
                item_obj.save()
        back_url = request.GET.get('back_url')
        return redirect(back_url)

@login_required(login_url='/myadmin/signin/')
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
            categories_list = item_models.get_data_list(
                item_models.Categories,
                current_page,
                search_value
            )
            categories_count = item_models.Categories. \
                get_categories_count(search_value)
        else:
            categories_list = item_models.Categories. \
                get_list_categories(current_page)
            categories_count = item_models.Categories. \
                get_categories_count()

        return my_render(
            request,
            'item/a_categorie_manage.html',
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


@login_required(login_url='/myadmin/signin/')
def add_categorie(request):
    categorie_choices = dict(item_models.Categories.type_choices)
    if request.method == 'GET':
        return my_render(
            request,
            'item/a_add_categorie.html',
            categorie_choices = categorie_choices,
        )
    else:
        form = AddCategorieForm(request.POST)
        if not form.is_valid():
            return my_render(
                request,
                'item/a_add_categorie.html',
                form_errors = form.errors,
                categorie_choices = categorie_choices,
            )
        categorie = form.save()
        files = request.FILES
        if files:
            file_obj = files.get('categorie_image')
            if not os.path.exists(settings.MEDIA_ROOT,):
                os.makedirs(settings.MEDIA_ROOT,)
            data = photo.save_upload_photo(
                file_obj,
                settings.MEDIA_ROOT,
            )
            if data:
                categorie.photo_id = data['photo_id']
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


@login_required(login_url='/myadmin/signin/')
def editor_categorie(request):
    categorie_id = request.GET.get('categorie_id')
    categorie = item_models.Categories.get_categorie_by_id(categorie_id)
    form_data = model_to_dict(categorie)
    categorie_choices = dict(item_models.Categories.type_choices)
    if request.method == 'GET':
        return my_render(
            request,
            'item/a_add_categorie.html',
            form_data = form_data,
            categorie_choices = categorie_choices,
        )
    else:
        form = EditorCategorieForm(request.POST)
        if not form.is_valid():
            return my_render(
                request,
                'item/a_add_categorie.html',
                form_errors = form.errors,
                categorie_choices = categorie_choices,
            )
        form.update(categorie_id)
        files = request.FILES
        if files:
            file_obj = files.get('categorie_image')
            if not os.path.exists(settings.MEDIA_ROOT,):
                os.makedirs(settings.MEDIA_ROOT,)
            data = photo.save_upload_photo(
                file_obj,
                settings.MEDIA_ROOT,
            )
            if data:
                categorie.photo_id = data['photo_id']
                categorie.save()
        back_url = request.GET.get('back_url')
        return redirect(back_url)

@login_required(login_url='/myadmin/signin/')
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
            'item/a_item_comment_manage.html',
            current_page = current_page,
            search_value = value,
            filter_args = filter_args,
            item_comments_list = item_comments_list,
            count = count,
        )

@login_required(login_url='/myadmin/signin/')
def item_comment_image_manage(request):
    if request.method == 'GET':
        comment_id = request.GET.get('comment_id')
        comment_image_list = item_models.CommentImages.get_comment_image_obj_by_id(comment_id)
        return my_render(
            request,
            'item/a_editor_comment_image.html',
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


@login_required(login_url='/myadmin/signin/')
def edit_item_comment(request):
    comment_id = request.GET.get('comment_id')
    form_data = item_models.ItemComments.get_item_comment_by_id(comment_id)
    if request.method == 'GET':
        return my_render(
            request,
            'item/a_editor_comment.html',
            form_data = form_data,
        )
    else:
        form = EditorItemCommentForm(request.POST)
        if not form.is_valid():
            return my_render(
                request,
                'item/a_editor_comment.html',
                form_data = form_data,
            )
        form.update(comment_id)
        back_url = request.GET.get('back_url')
        return redirect(back_url)


def create_brand(request):
    obj = item_models.Items.objects.values('brand_name').annotate(c=Count('brand_name'))
    brand_model = item_models.Brands
    brand_model.objects.all().delete()
    for i in obj:
        item_models.create_model_data(
            brand_model,
            {'cn_name': i['brand_name']}
        )
    return redirect('/myadmin/brand_manage/')