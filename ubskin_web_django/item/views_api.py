import os
import random

from django.views.decorators.csrf import csrf_exempt
from django import forms
from django.http import JsonResponse
from django.conf import settings

from ubskin_web_django.common import photo
from ubskin_web_django.common import decorators
from ubskin_web_django.item import models as item_models


@decorators.api_authenticated
def get_item_info(request):
    return_value  = {
        'status': 'error',
        'message': '',
        'data': '',
    }
    if request.method == 'GET':
        current_page = request.GET.get('page', 1)
        items = item_models.Items.get_items_list_for_api(current_page)
        return_value['status'] = 'success'
        return_value['data'] = items
        return JsonResponse(return_value)

@decorators.api_authenticated
def api_get_categories(request):
    return_value  = {
        'status': 'error',
        'message': '',
        'data': '',
    }
    if request.method == 'GET':
        data_list = item_models.Categories.get_categoreis_for_api()
        return_value['status'] = 'success'
        return_value['data'] = data_list
        return JsonResponse(return_value)

@decorators.api_authenticated
def filter_items(request):
    return_value  = {
        'status': 'error',
        'message': '',
        'data': '',
    }
    if request.method == 'GET':
        categorie_id = request.GET.get('categorie_id')
        current_page = request.GET.get('page', 1)
        datas = item_models.Items. \
            get_items_by_categorie_id(categorie_id, current_page)
        return_value['status'] = 'success'
        return_value['data'] = datas
        return JsonResponse(return_value)

@decorators.api_authenticated
def get_item_comment(request):
    return_value  = {
        'status': 'error',
        'message': '',
        'data': '',
    }
    if request.method == 'GET':
        item_id = request.GET.get('item_id', 1)
        current_page = request.GET.get('page', 1)
        item_comment_data = item_models.ItemComments. \
            get_item_comment_by_item_id(item_id, current_page)
        return_value['status'] = 'success'
        return_value['data'] = item_comment_data
        return JsonResponse(return_value)


class CreateCommentForm(forms.ModelForm):
    class Meta:
        model = item_models.ItemComments
        fields = ('member_id', 'item_id', 'comment_content',)

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(CreateCommentForm, self).save(commit=False)
        if commit:
            user.save()
        return user


@decorators.api_authenticated
@csrf_exempt
def create_item_comment(request):
    return_value = {
        'status': 'error',
        'message': '',
        'data': '',
    }
    if request.method == 'POST':
        form = CreateCommentForm(request.POST)
        if not form.is_valid():
            return_value['message'] = list(form.errors.values())[0]
            return JsonResponse(return_value)
        obj = form.save()
        comment_image_list = []
        files = request.FILES
        if files:
            for i in files:
                file_obj = files[i]
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
                    'comment'
                )
                if data:
                    data['comment_id'] = obj.comment_id
                    comment_image_list.append(data)
            else:
                item_models.CommentImages. \
                create_many_comment_image(comment_image_list)
        return_value['status'] = 'success'
        return JsonResponse(return_value)