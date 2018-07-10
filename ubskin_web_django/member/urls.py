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
    path('myadmin/', views.index),
]

urlpatterns += [
    path('js/create_member/', views_js.create_member, name='create_member'),
    path('js/delete_member/', views_js.delete_member, name='delete_member'),
    path('js/edit_member/', views_js.editor_member, name='edit_member'),
]

urlpatterns += [
    path('api/signin/', views_api.signin),
    path('api/signin_out/', views_api.signin_out),
    path('api/register/', views_api.register),
    path('api/wx_signin/', views_api.wx_signin),
    path('api/check_is_staff/<str:openid>/', views_api.check_is_staff),
]