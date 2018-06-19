from django.urls import path

from my_admin import views_api

urlpatterns = [
    path('get_item_info/', views_api.get_item_info),
    path('get_categories/', views_api.api_get_categories),
    path('filter_items/', views_api.filter_items),
    path('get_item_comment/', views_api.get_item_comment),
    path('create_item_comment/', views_api.create_item_comment),
    path('signin/', views_api.signin),
    path('signin_out/', views_api.signin_out),
    path('register/', views_api.register),
]