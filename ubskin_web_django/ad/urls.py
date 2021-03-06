from django.urls import path

from ubskin_web_django.ad import views
from ubskin_web_django.ad import views_js
from ubskin_web_django.ad import views_api


urlpatterns = [
    path('myadmin/campaigns_manage/', views.campaigns_manage, name='campaigns_manage'),
    path('myadmin/add_campaign/', views.add_campaign, name='add_campaign'),
    path('myadmin/editor_campaign/', views.editor_campaign, name='editor_campaign'),
]

urlpatterns += [
    path('js/delete_campaigns/', views_js.delete_campaigns, name='delete_campaigns')
]

urlpatterns += [
    path('api/get_campaigns/', views_api.get_campaigns),
    path('api/get_items_by_campaign_id/', views_api.get_items_by_campaign_id),
]
