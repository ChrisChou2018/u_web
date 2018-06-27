from django.urls import path

from ubskin_web_django.order import views
from ubskin_web_django.order import views_js
from ubskin_web_django.order import views_api


urlpatterns = [
    path('order_manage/', views.order_manage, name='order_manage'),
    path('item_qr_Code_manage/', views.item_qr_Code_manage, name='item_qr_Code_manage'),
    path('reve_manage/', views.recv_manage, name='recv_manage'),
    path('stock_batch/', views.stock_batch, name='stock_batch')
]

urlpatterns += [
    path('js/create_recv/', views_js.create_recv, name='create_recv'),
    path('js/set_recv_watch/', views_js.set_recv_watch, name='set_recv_watch'),
    path('js/delete_recv/', views_js.delete_recv, name='delete_recv'),
    path('js/edit_recv/', views_js.edit_recv, name='edit_recv'),
    path('js/get_recv_addr/', views_js.get_reve_addr, name='get_recv_addr'),
    path('js/get_item_info_by_code/', views_js.get_item_info_by_code, name='get_item_info_by_code'),
    path('js/create_stock_bach/', views_js.create_stock_bach, name="create_stock_bach"),
    path('js/a_jm_stock_batch_info/', views_js.jm_stock_batch_info, name='a_jm_stock_batch_info')
]

urlpatterns += [
    path('api/get_recv/', views_api.get_recv),
    path('api/create_stock_batch_api/', views_api.create_stock_batch_api),
    path('api/item_code/', views_api.item_code),
    path('create_recv/', views_api.create_recv)
]