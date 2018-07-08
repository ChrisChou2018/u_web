import os

from django.http import JsonResponse
from django.conf import settings

from ubskin_web_django.item import models as item_models
from ubskin_web_django.common import photo
from ubskin_web_django.common import decorators


@decorators.js_authenticated
def delete_items(request):
    item_id_list = request.POST.getlist('item_id_list[]')
    item_models.Items.delete_item_by_item_ids(item_id_list)
    return JsonResponse({'status': 'success'})

@decorators.js_authenticated
def item_image_create(request):
    return_value = {
        'status':'error',
        'message':'',
    }
    if request.method == "POST":
        files_dict = request.FILES
        image_type = request.POST.get('image_type')
        item_id = request.POST.get('item_id')
        for k in files_dict:
            if not os.path.exists(settings.MEDIA_ROOT):
                os.makedirs(settings.MEDIA_ROOT)
            data = photo.save_upload_photo(
                files_dict[k],
                settings.MEDIA_ROOT,
            )
            if data:
                data.update({
                    'image_type': image_type,
                    'item_id': item_id,
                    'status': 'normal'
                })
                item_models.ItemImages.create_item_image(data)
                if int(image_type) == 0:
                    item_obj = item_models.get_model_obj_by_pk(
                    item_models.Items,
                    item_id
                    )
                    item_obj.photo_id = data.get('photo_id')
                    item_obj.save()
            else:
                return_value['message'] = '上传失败'
                return JsonResponse(return_value)
        else:
            return_value['result'] = 'success'
            return JsonResponse(return_value)

@decorators.js_authenticated
def delete_item_images(request):
    image_id_list = request.POST.getlist('image_id_list[]')
    item_models.ItemImages. \
        update_images_by_image_id_list(image_id_list, {'status': 'deleted'})
    return JsonResponse({'status': 'success'})

@decorators.js_authenticated
def delete_brands(request):
    if request.method == 'POST':
        brand_ids_list = request.POST.getlist('brand_ids_list[]')
        item_models.Brands.delete_brands_by_id_list(brand_ids_list)
        return JsonResponse({'status': 'success'})

@decorators.js_authenticated
def delete_categories(request):
    if request.method == 'POST':
        categorie_ids_list = request.POST.getlist('categorie_ids_list[]')
        item_models.Categories.delete_categories_by_id_list(categorie_ids_list)
        return JsonResponse({'status': 'success'})

@decorators.js_authenticated
def delete_item_comments(request):
    if request.method == 'POST':
        comment_ids_list = request.POST.getlist('comment_ids_list[]')
        item_models.ItemComments.delete_comment_by_id_list(comment_ids_list)
        return JsonResponse({'status': 'success'})