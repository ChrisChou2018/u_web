from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.utils.six import BytesIO
from rest_framework.parsers import JSONParser

from my_admin import serializers
from my_admin import item_models


@api_view(['GET'])
def get_item_info(request):
    if request.method == 'GET':
        current_page = request.GET.get('page', 1)
        items = item_models.Items.get_items_list_for_api(current_page)
        serializer = serializers.ItemSerializer(items, many=True)
        return Response(serializer.data)

@api_view(['GET'])
def get_item_image(request):
    if request.method == 'GET':
        item_id = request.GET.get('item_id')
        datas = item_models.ItemImages.get_images_by_itemid(item_id)
        serializer = serializers.ItemImagesSerializer(datas, many=True)
        return Response(serializer.data)

@api_view(['GET'])
def api_get_categories(request):
    if request.method == 'GET':
        data_list = item_models.Categories.get_categoreis_for_api()
        return Response(data_list)

@api_view(['GET'])
def filter_items(request):
    if request.method == 'GET':
        categorie_id = request.GET.get('categorie_id')
        current_page = request.GET.get('page', 1)
        datas = item_models.Items. \
            get_items_by_categorie_id(categorie_id, current_page)
        serializer = serializers.ItemSerializer(datas, many=True)
        return Response(serializer.data)

@api_view(['GET'])
def get_item_comment(request):
    if request.method == 'GET':
        item_id = request.GET.get('item_id', 1)
        current_page = request.GET.get('page', 1)
        item_comment_data = item_models.ItemComments. \
            get_item_comment_by_item_id(item_id, current_page)
        return Response(item_comment_data)

@api_view(['POST'])
def create_item_comment(request):
    pass