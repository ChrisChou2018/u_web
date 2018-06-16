from rest_framework import serializers
from my_admin import item_models
from my_admin import member_models



class MemberSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = member_models.Member
        fields = ('member_name', 'member_id', 'telephone', 'is_admin')

# class ItemsSerializer(serializers.HyperlinkedModelSerializer):
#     class Meta:
#         model = item_models.Items
#         fields = (

#         )