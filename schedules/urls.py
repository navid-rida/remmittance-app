from django.urls import path

from . import views

urlpatterns = [
    #path('', views.index, name='index'),
    
    path('add/rates', views.RateCreate.as_view(), name='add_rate'),
    path('report/rit', views.remittance_rit_list, name='download_rit'),
    
]
