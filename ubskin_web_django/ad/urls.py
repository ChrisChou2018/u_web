from django.urls import path

from ubskin_web_django.ad import views
from ubskin_web_django.ad import views_js
from ubskin_web_django.ad import views_api


urlpatterns = [
   path('myadmin/campaigns_manage/', views.campaigns_manage, name='campaigns_manage'),
]

urlpatterns += [
    
]

urlpatterns += [
    
]
