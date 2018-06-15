from django.urls import path
from my_admin import views
from my_admin import views_js


urlpatterns = [
    # path('admin/', admin.site.urls),
    path('signin/', views.member_signin),
    path('index/', views.index),
    path('signout/', views.member_signout),
    path('change_password/', views.change_pass),
    path('member_manage/', views.member_manage),
    path('item_manage/', views.items_manage),
    path('add_item/', views.add_item),
    path('editor_item/', views.editor_item),
    path('item_image_manage/', views.item_image_manage),
    path('brand_manage/', views.brand_manage),
    path('add_brand/', views.add_brand),
    path('editor_brand/', views.editor_brand),
    path('categorie_manage/', views.categorie_manage),
    path('add_categorie/', views.add_categorie),
    path('editor_categorie/', views.editor_categorie),
    path('', views.index),
]

urlpatterns += [
    path('js/create_member/', views_js.create_member),
    path('js/delete_member/', views_js.delete_member),
    path('js/edit_member/', views_js.editor_member),
    path('js/delete_items/', views_js.delete_items),
    path('js/item_image_create/', views_js.item_image_create),
    path('js/delete_item_images/', views_js.delete_item_images),
    path('js/delete_brands/',  views_js.delete_brands),
    path('js/delete_categories/', views_js.delete_categories),
]