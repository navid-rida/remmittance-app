from django.db.models import Sum, Count
from django.utils import timezone
from .models import Remmit, Branch, ExchangeHouse, Payment, Branch
import pandas as pd
from .DataModels import *

year = timezone.now().date().year

################################ Branchwise remittance count and sum ####################################

def branch_remittance_summary(branch_list, year=None, month=None, start_date=None, end_date= None, exchange_house=None):
    """ Takes branch list, exchange house, date range as args
        and return DataFrame containing list of branches, remittance
        amount sum and count"""
    #sum_list = []  #### will countain list of sums from each branch
    #name_list = [] #### will countain list of name of each branch
    #count_list = [] #### will countain list of counts from each branch
    branch_total_list = []
    for branch in branch_list:
        #name_list.append(branch.name)
        code = branch.code
        name = branch.name
        sum, count = branch.branch_total(year, month, start_date, end_date, exchange_house)
        branch_dict = {'code': code,
                        'name': name,
                        'count': count,
                        'sum': sum,}
        #sum_list.append(sum)
        #count_list.append(count)
        branch_total_list.append(branch_dict)
    """total_dict = {'name': name_list,
                'sum': sum_list,
                'count': count_list}"""
    #total_df = branch_total_list
    return branch_total_list



#######################################################################################################################

def group_branchwise(year,month, ex_column=False, house=None):
    """ Returns number and sum of
    remittance for each branch"""
    if ex_column:
        q = Payment.objects.filter(date_settle__year=year,date_settle__month=month,requestpay__remittance__exchange=house).values('requestpay__remittance__branch__code','requestpay__remittance__branch__name').annotate(sum = Sum('requestpay__remittance__amount'), number = Count('requestpay__remittance__amount'), exchange=F('requestpay__remittance__exchange__name')).order_by('requestpay__remittance__branch__code')
    else:
        q = Payment.objects.filter(date_settle__year=year,date_settle__month=month).values('requestpay__remittance__branch__code','requestpay__remittance__branch__name').annotate(sum = Sum('requestpay__remittance__amount'), number = Count('requestpay__remittance__amount')).order_by('requestpay__remittance__branch__code')
    df = pd.DataFrame(q)
    br = qset_to_df(Branch.objects.all())
    df = df.merge(br, left_on='requestpay__remittance__branch__code', right_on='code', how='outer')
    df = df[['code','name','sum','number']]
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
    return dc
