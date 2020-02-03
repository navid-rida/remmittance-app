from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('add/remmittance/<int:pk>/', views.RemmitCreate.as_view(), name='remmit-create'),
    path('add/remmittancefull/<int:pk>/', views.RemmitInfoCreate.as_view(), name='remmit-create-with-payment'), # submits a remittance info only assuming payment is done
    path('edit/remmittance/<int:pk>/', views.RemmitUpdate.as_view(), name='remmit-update'),
    path('edit/remmittancefull/<int:pk>/', views.RemmitInfoUpdate.as_view(), name='remmit-update-with-payment-screenshot'),
    path('show/remmittance', views.show_rem, name='show_rem'),
    path('show/claim', views.show_claim, name='show_claim'),
    path('show/requests', views.show_req, name='show_req'),
    path('show/select-entry', views.select_rem_list, name='select_rem_list'),
    path('show/select-cash-incentive', views.select_cash_incentive_list, name='select-cash-incentive'),
    #path('show/mark-settle', views.mark_rem_list, name='mark_rem_list'),
    path('mark-settle', views.mark_settle_all, name='mark_settle_all'),
    #path('show/cash-incentive-mark-settle', views.mark_cash_incentive_list, name='mark_cash_incentive_list'),
    #path('download/daily-remmittance-csv', views.download_bb_excel, name='download_csv'),
    path('download/daily-remmittance-exc', views.download_selected_excel, name='download_exc'),
    path('download/cash_incentive_excel', views.download_cash_incentive_excel, name='cash_incentive_excel'),
    #path('download/daily-remmittance-mark-settle', views.mark_settle, name='mark_settle'),
    #path('download/daily-cash-incentive-mark-settle', views.cash_incentive_mark_settle, name='cash_incentive_mark_settle'),
    path('search/client', views.search_receiver, name='search_client'),
    path('search/remittance', views.search_remittance, name='search_remittance'),
    path('add/client', views.ReceiverCreate.as_view(), name='add_client'),
    path('add/claim', views.ClaimCreate.as_view(), name='add_claim'),
    path('edit/client/<int:pk>/', views.ReceiverUpdate.as_view(), name='receiver_update'),
    path('add/req/<int:pk>/', views.ReceiverCreate.as_view(), name='add_req'),
    path('add/payment/<int:pk>/', views.payment_confirm, name='payment-confirm'),
    ########################## Details #########################################
    path('detail/req/<int:pk>/', views.RequestpayDetailView.as_view(), name='requestpay-detail'),
    path('detail/remittance/<int:pk>/', views.RemmitDetailView.as_view(), name='remitt-detail'),
    path('detail/claim/<int:pk>/', views.ClaimDetailView.as_view(), name='claim-detail'),
    path('resubmit/req/<int:pk>/', views.request_resubmit, name='requestpay-resubmit'),
    path('detail/mark_paid/<int:pk>/', views.pay_unpaid_incentive, name='pay_unpaid_incentive'),
    path('detail/forward_claim/<int:pk>/', views.forward_claim, name='forward_claim'),
    path('detail/mark_resolved/<int:pk>/', views.mark_resolved, name='mark_resolved'),
    ############################## USer Regestration & Authentication #########################
    path('signup', views.signup, name='signup'),
    ############################ report ################################
    path('summary', views.summary_report, name='summary'),
    path('cash_incentive_bb_statement', views.monthly_cash_incentive_bb_statement, name='cash_incentive_bb_statement'),
    path('daily_remittance_bb_statement', views.daily_remittance_bb_statement, name='daily_remittance_bb'),
]
