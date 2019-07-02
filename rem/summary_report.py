from django.db.models import Sum, Count
from django.utils import timezone
from .models import Remmit, Branch, ExchangeHouse
import pandas as pd
from .DataModels import *

year = timezone.now().date().year

def group_branchwise(year,month, ex_column=False, house=None):
    """ Returns number and sum of
    remittance for each branch"""
    if ex_column:
        q = Remmit.objects.filter(date_create__year=year,date_create__month=month).values('branch__code','branch__name').annotate(sum = Sum('amount'), number = Count('amount'), exchange=F('exchange__name')).order_by('branch__code')
    else:
        q = Remmit.objects.filter(date_create__year=year,date_create__month=month).values('branch__code','branch__name').annotate(sum = Sum('amount'), number = Count('amount')).order_by('branch__code')
    df = pd.DataFrame(q)
    br = qset_to_df(Branch.objects.all())
    df = df.merge(br, left_on='branch__code', right_on='code', how='outer')
    return df


def get_total_branch_summary(year, month):
    """ gets branch remiittance total amount
    and number for exchange house"""
    #q = Remmit.objects.filter(date_create__year=year,date_create__month=month)
    df = group_branchwise(qset=q)
    return df

def get_ex_wise_branch_summary():
    year = '2019'
    month = 6
    exc = ExchangeHouse.objects.all()
    dc = dict()
    for house in exc:
        name=house.name
        df = group_branchwise(year=year,month=month,ex_column=True,house=house)
        dc[name] = df
