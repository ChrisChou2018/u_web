from django.urls import path
from ubskin_web_django.member import views
from ubskin_web_django.member import views_js
from ubskin_web_django.member import views_api


urlpatterns = [
    path('myadmin/signin/', views.member_signin, name='signin'),
    path('myadmin/index/', views.index, name='index'),
    path('myadmin/signout/', views.member_signout, name='signout'),
    path('myadmin/change_password/', views.change_pass, name='change_password'),
    path('myadmin/member_manage/', views.member_manage, name='member_manage'),
    path('myadmin/user_order_manage/', views.user_order_manage, name="user_order_manage"),
    path('myadmin/recv_addr_manage/', views.recv_addr, name='recv_addr_manage'),
    path('myadmin/out_order_manage/', views.out_order_manage, name='out_order_manage'),
    path('myadmin/', views.index),
]

urlpatterns += [
    path('js/create_member/', views_js.create_member, name='create_member'),
    path('js/delete_member/', views_js.delete_member, name='delete_member'),
    path('js/edit_member/', views_js.editor_member, name='edit_member'),
    path('js/jm_recv_addr_info/', views_js.jm_recv_addr_info, name='jm_recv_addr_info'),
]

urlpatterns += [
    path('api/signin/', views_api.signin),
    path('api/signin_out/', views_api.signin_out),
    path('api/register/', views_api.register),
    path('api/wx_signin/', views_api.wx_signin),
    path('api/check_is_staff/<str:openid>/', views_api.check_is_staff),
    path('api/create_recv_addr/', views_api.create_recv_addr),
    path('api/get_recv_addr/', views_api.get_recv_addr),
    path('api/delete_recv_addr/', views_api.delete_recv_addr),
    path('api/update_recv_addr/', views_api.update_recv_addr),
    path('api/create_user_order/', views_api.create_user_order),
    path('api/get_user_order/', views_api.get_user_order),
    path('api/get_user_orer_info/<str:order_num>/', views_api.get_user_order_info),
]