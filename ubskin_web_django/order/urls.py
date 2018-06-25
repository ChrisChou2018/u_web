from django.urls import path
from ubskin_web_django.order import views
from ubskin_web_django.order import views_js
from ubskin_web_django.order import views_api


urlpatterns = [
    path('order_manage/', views.order_manage, name='order_manage'),
    path('item_qr_Code_manage/', views.item_qr_Code_manage, name='item_qr_Code_manage'),
    path('reve_manage/', views.recv_manage, name='recv_manage'),
    path('out_order/', views.out_order, name='out_order')
]

urlpatterns += [
    path('js/create_recv/', views_js.create_recv, name='create_recv'),
    path('js/set_recv_watch/', views_js.set_recv_watch, name='set_recv_watch'),
    path('js/delete_recv/', views_js.delete_recv, name='delete_recv'),
    path('js/edit_recv/', views_js.edit_recv, name='edit_recv'),
    path('js/get_recv_addr/', views_js.get_reve_addr, name='get_recv_addr'),
    path('js/get_item_info_by_code/', views_js.get_item_info_by_code, name='get_item_info_by_code'),
    path('js/create_out_order/', views_js.create_out_order, name="create_out_order"),
    path('js/jm_out_order_item_info/', views_js.jm_out_order_item_info, name='jm_out_order_item_info')
]