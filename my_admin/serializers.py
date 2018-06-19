from rest_framework import serializers
from my_admin import item_models
from my_admin import member_models



class MemberSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = member_models.Member
        fields = ('member_name', 'member_id', 'telephone', 'is_admin')


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = item_models.Items
        fields = ( 
            "item_name", "item_info", "item_code",
            "item_barcode", "price", "current_price",
            "foreign_price", "key_word", "origin",
            "shelf_life", "capacity", "specifications_type_id",
            "for_people", "weight", "brand_id",
            "categories_id", "item_id"
        )


class ItemImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = item_models.ItemImages
        fields = (
            'image_id', 'item_id', 'image_type',
            'image_path', 'file_size', 'resolution',
            'file_type'
        )




    
