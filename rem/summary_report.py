from django.db.models import Sum, Count
from django.utils import timezone
from .models import Remmit, Branch, ExchangeHouse, Payment, Branch
import pandas as pd
from .DataModels import *

year = timezone.now().date().year

################################ Branchwise remittance count and sum ####################################

def exchange_housewise_remittance_summary(list, year=None, month=None, start_date=None, end_date= None, exchange_house=None, BranchBooth=None):
    """ Takes branch list, exchange house, date range as args
        and return DataFrame containing list of branches, remittance
        amount sum and count"""
    #sum_list = []  #### will countain list of sums from each branch
    #name_list = [] #### will countain list of name of each branch
    #count_list = [] #### will countain list of counts from each branch
    branch_booth_total_list = []
    for branch_or_booth in list:
        #name_list.append(branch.name)
        code = branch_or_booth.code
        name = branch_or_booth.name
        sum, count = branch_or_booth.total_sum_count(year, month, start_date, end_date, exchange_house,BranchBooth)
        branch_dict = {'code': code,
                        'name': name,
                        'count': count,
                        'sum': sum,}
        #sum_list.append(sum)
        #count_list.append(count)
        branch_booth_total_list.append(branch_dict)
    """total_dict = {'name': name_list,
                'sum': sum_list,
                'count': count_list}"""
    #total_df = branch_total_list
    return branch_booth_total_list

def cash_incentive_bb_statement(qset):
    q = qset
    ben_name_address=[]
    ben_id=[]
    ben_acc=[]
    bank_name=[]
    sender_name=[]
    sender_occupation=[]
    exchange_house=[]
    date_sending_remittance=[]
    fc_amount=[]
    exchange_rate=[]
    bdt_amount=[]
    trn_type=[]
    cash_incentive_amount=[]
    date_remittance_paid=[]
    remarks=[]
    reference=[]
    branch=[]
    dealing_offical=[]
    dealing_cell=[]
    for r in q:
        ben_name_address.append(r.remittance.receiver.name.upper())
        ben_id.append(r.remittance.receiver.idno)
        ben_acc.append(r.remittance.receiver.ac_no) #to change
        bank_name.append("NRB COMMERCIAL BANK LTD.")
        sender_name.append(r.remittance.sender.upper())
        sender_occupation.append(r.remittance.get_sender_occupation_display().upper() if r.remittance.sender_occupation else None)
        exchange_house.append(r.remittance.exchange.name if r.remittance.is_thirdparty_remittance() else r.remittance.sender_bank.name)
        date_sending_remittance.append(r.remittance.date_sending)
        fc_amount.append(float(r.get_fc_amount())) #to be changed mandatory status
        exchange_rate.append(r.get_exchange_rate()) #to be changed mandatory status
        bdt_amount.append(r.get_bdt_amount()) #to_change
        trn_type.append(r.remittance.get_ci_trn_type())
        cash_incentive_amount.append(r.cash_incentive_amount)
        date_remittance_paid.append(r.date_cash_incentive_settlement)
        remarks.append('')
        reference.append(r.remittance.reference)
        branch.append(r.remittance.branch.name.upper())
        dealing_offical.append(r.remittance.created_by.first_name.upper()+" "+r.remittance.created_by.last_name.upper())
        dealing_cell.append(r.remittance.created_by.employee.cell)
    dct = {"Benificiary Name & Address": ben_name_address,
            "Identification": ben_id,
            "Benificiary Account": ben_acc,
            "Bank Name": bank_name,
            "Name of Sender": sender_name,
            "Occupation of Sender": sender_occupation,
            "Exchange House":exchange_house,
            "Date of Sending Remittance":date_sending_remittance,
            "FC Amount":fc_amount,
            "Exchange rate": exchange_rate,
            "BDT Amount": bdt_amount,
            "Type":trn_type,
            "Incentive Amount": cash_incentive_amount,
            "Date of Payment": date_remittance_paid,
            "Remrks": remarks,
            "Reference": reference,
            "Branch": branch,
            "Dealing Official": dealing_offical,
            "Cell Phone": dealing_cell,
            }
    df = pd.DataFrame(dct)
    df['FC Amount'] = df['FC Amount'].round(2)
    return df

#def daily_remittance_bb_statement(qset):

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
