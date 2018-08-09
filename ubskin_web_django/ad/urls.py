from django.urls import path

from ubskin_web_django.ad import views
from ubskin_web_django.ad import views_js
from ubskin_web_django.ad import views_api


urlpatterns = [
   path('myadmin/campaigns_manage/', views.campaigns_manage, name='campaigns_manage'),
   path('myadmin/add_campaign/', views.add_campaign, name='add_campaign'),
   path('myadmin/editor_campaign/', views.editor_campaign, name='editor_campaign')
]

urlpatterns += [
    
]

urlpatterns += [
    
]
