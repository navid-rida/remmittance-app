from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('add/remmittance', views.RemmitCreate.as_view(), name='remmit-create'),
    path('edit/remmittance/<int:pk>/', views.RemmitUpdate.as_view(), name='remmit-update'),
    path('show/remmittance', views.show_rem, name='show_rem'),
    path('show/select-entry', views.select_rem_list, name='select_rem_list'),
    path('show/mark-settle', views.mark_rem_list, name='mark_rem_list'),
    #path('download/daily-remmittance-csv', views.download_bb_excel, name='download_csv'),
    path('download/daily-remmittance-exc', views.download_selected_excel, name='download_exc'),
    path('download/daily-remmittance-mark-settle', views.mark_settle, name='mark_settle'),
]
