from django.urls import path

from ubskin_web_django.item import views
from ubskin_web_django.item import views_js
from ubskin_web_django.item import views_api


urlpatterns = [
    path('admin/item_manage/', views.items_manage, name='item_manage'),
    path('admin/add_item/', views.add_item, name='add_item'),
    path('admin/editor_item/', views.editor_item, name='editor_item'),
    path('admin/item_image_manage/', views.item_image_manage, name='item_image_manage'),
    path('admin/brand_manage/', views.brand_manage, name='brand_manage'),
    path('admin/add_brand/', views.add_brand, name='add_brand'),
    path('admin/editor_brand/', views.editor_brand, name='editor_brand'),
    path('admin/categorie_manage/', views.categorie_manage, name='categorie_manage'),
    path('admin/add_categorie/', views.add_categorie, name='add_categorie'),
    path('admin/editor_categorie/', views.editor_categorie, name='editor_categorie'),
    path('admin/item_comment_manage/', views.item_comment_manage, name='item_comment_manage'),
    path('admin/edit_item_comment/', views.edit_item_comment, name='edit_item_comment'),
    path('admin/comment_image_manage/', views.item_comment_image_manage, name='comment_image_manage'),
]

urlpatterns += [
    path('js/delete_items/', views_js.delete_items, name='delete_items'),
    path('js/item_image_create/', views_js.item_image_create, name='item_image_create'),
    path('js/delete_item_images/', views_js.delete_item_images, name='delete_item_images'),
    path('js/delete_brands/',  views_js.delete_brands, name='delete_brands'),
    path('js/delete_categories/', views_js.delete_categories, name='delete_categories'),
    path('js/delete_item_comments/', views_js.delete_item_comments, name='delete_item_comments'),
]

urlpatterns += [
    path('api/get_item_info/', views_api.get_item_info),
    path('api/get_categories/', views_api.api_get_categories),
    path('api/filter_items/', views_api.filter_items),
    path('api/get_item_comment/', views_api.get_item_comment),
    path('api/create_item_comment/', views_api.create_item_comment),
    path('api/get_item_info_by_code/', views_api.get_item_info_by_code),
]
