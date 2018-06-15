
from rest_framework import viewsets
from my_admin.serializers import MemberSerializer

from my_admin import item_models
from my_admin import member_models



class MemberViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = member_models.Member.objects.all()
    serializer_class = MemberSerializer