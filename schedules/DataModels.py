from locale import currency
from rem.models import Remmit,Receiver, CashIncentive, ExchangeHouse, Country
from .models import *
import pandas as pd
from datetime import datetime, date,timedelta
import io
from django.db.models import Q #IntegerField, F, Value, 
#from .validators import *
from django.core.exceptions import ValidationError
#from rem.models import *
from rem.DataModels import qset_to_df
from decimal import Decimal
from django.utils import timezone
####################### fuzzywuzzy imports ##################################
#from .search import remittance_search
from fuzzywuzzy import fuzz
from fuzzywuzzy import process



def gender_abbr(gender_short):
    if gender_short=='M':
        return 'Male'
    elif gender_short=='F':
        return 'Female'
    else:
        return 'OTHER'
    
def get_usd_rate(report_date=timezone.now().date()):
    usd_rate = Rate.objects.filter(currency__short= 'USD').filter(date__lte=report_date).last()
    return usd_rate.rate

def remittance_rit(qset):
    if qset.exists():
        rem_qset = Remmit.objects.filter(cashincentive__in = qset)
        #Takes remittance quesryset and returns RIT Dataframe
        remit_df = qset_to_df(rem_qset.filter(entry_category='P', date_cash_incentive_settlement__isnull=False))
        remit_df['date_create'] = pd.to_datetime(remit_df['date_create']).dt.date
        receiver_df = qset_to_df(Receiver.objects.filter(remmit__in=rem_qset).distinct())
        e_df = qset_to_df(ExchangeHouse.objects.filter(remmit__in=rem_qset).distinct())
        country_df = qset_to_df(Country.objects.filter(remmit__in=rem_qset).distinct())
        currency_qset = Currency.objects.filter(remmit__in=rem_qset).distinct()
        currency_df = qset_to_df(currency_qset)
        rate_qset = Rate.objects.filter(currency__in=currency_qset)
        rate_df = qset_to_df(rate_qset)
        usd_rate = qset_to_df(Rate.objects.filter(currency__short= 'USD').filter(date__lte=timezone.now().date()))['rate'].values[0]
        
        cashin_qset = CashIncentive.objects.filter(remittance__in=qset, entry_category='P').distinct()
        cashin_df = qset_to_df(cashin_qset)
        
        df = pd.merge(receiver_df, remit_df, how = 'outer', left_on='id', right_on='receiver_id', suffixes=('_receiver', '_remittance'))
        df['receiver_gender'] = df['gender'].apply(gender_abbr)

        df['bank'] = 'NRB COMMERCIAL BANK LTD.'

        df['trn_type'] = 'SUBAGENT_CASHPICKUP'

        df['sender_gender'] = df['sender_gender'].apply(gender_abbr)

        df = df.merge(country_df, how = 'outer', left_on='rem_country_id', right_on='id',suffixes=('', '_country'))

        df = df.merge(e_df, how = 'outer', left_on='exchange_id', right_on='id',suffixes=('', '_exchange'))

        df['date_sending'] = pd.to_datetime(df['date_sending']).dt.strftime("%d-%b-%y").str.upper()

        df = df.merge(currency_df, how = 'outer', left_on='currency_id', right_on='id', suffixes=('', '_currency'))

        df = df.merge(rate_df, how = 'left', left_on = ['id_currency','date_create'], right_on=['currency_id','date'], suffixes=('','_rate'))

        df['amt_bdt'] = df.apply(lambda x: Decimal(x['amount']) * Decimal(x['rate']) if x['rate']!=None else None, axis=1)
        df['amt_usd'] = df['amt_bdt']/get_usd_rate()
        
        df = df.merge(cashin_df, how = 'left', left_on='id_remittance', right_on='remittance_id', suffixes=('', '_cashin')) if not cashin_df.empty else df
        df['date_cash_incentive_paid_cashin'] = pd.to_datetime(df['date_cash_incentive_paid_cashin']).dt.strftime("%d-%b-%y").str.upper()
        
        return df[['reference','name','receiver_gender','idtype','idno','bank','trn_type', 'sender', 'sender_gender','sender_occupation','name_country','verbose_name', 'date_sending', 'amount','short','rate','amt_bdt','amt_usd','cash_incentive_amount_cashin', 'date_cash_incentive_paid_cashin']]
    else:
        df = pd.DataFrame()
        return df
    """name= []
    for q in qset:
        name.append(q.receiver.name)
        receiver_gender.append(q.receiver.gender)
        doc_type.append(q.receiver.idtype)
        doc_no.append(q.receiver.idno)
        bankname.append('NRB COMMERCIAL BANK LTD.')
        tr_type.append(q.get_ci_trn_type())"""

def cash_incentive_rit(qset):
    q = qset
    ben_name=[]
    gender=[]
    doc_type=[]
    id_no=[]
    bank_name=[]
    trn_type=[]
    sender_name=[]
    sender_gender=[]
    sender_occupation=[]
    source_country=[]
    exchange_house=[]
    date_sending_remittance=[]
    fc_amount=[]
    currency=[]
    exchange_rate=[]
    bdt_amount=[]
    usd_amount=[]
    cash_incentive_amount=[]
    date_cashincentive_paid=[]
    remarks=[]
    reference=[]
    branch=[]
    dealing_offical=[]
    dealing_cell=[]
    for r in q:
        ben_name.append(r.remittance.receiver.name.upper())
        gender.append(r.remittance.receiver.get_gender_display())
        doc_type.append(r.remittance.receiver.idtype) #to change
        id_no.append(r.remittance.receiver.idno)
        bank_name.append("NRB COMMERCIAL BANK LTD.")
        trn_type.append(r.remittance.get_ci_trn_type())
        sender_name.append(r.remittance.sender.upper())
        sender_gender.append(r.remittance.get_sender_gender_display())
        sender_occupation.append(r.remittance.get_sender_occupation_display().upper() if r.remittance.sender_occupation else None)
        source_country.append(r.remittance.rem_country.name)
        exchange_house.append(r.remittance.exchange.name if r.remittance.is_thirdparty_remittance() else "Other")
        date_sending_remittance.append(r.remittance.date_sending)
        fc_amount.append(r.get_fc_amount()) #to be changed mandatory status
        currency.append("USD" if r.remittance.currency.short=='BDT' else r.remittance.currency.short)
        exchange_rate.append(r.get_exchange_rate()) #to be changed mandatory status
        bdt_amount.append(r.get_bdt_amount()) #to_change
        usd_amount.append(r.get_usd_amount()) #to_change
        cash_incentive_amount.append(r.cash_incentive_amount)
        date_cashincentive_paid.append(r.date_cash_incentive_settlement)
        remarks.append('')
        reference.append(r.remittance.reference)
        branch.append(r.remittance.branch.name.upper())
        dealing_offical.append(r.remittance.created_by.first_name.upper()+" "+r.remittance.created_by.last_name.upper())
        dealing_cell.append(r.remittance.created_by.employee.cell)
    dct = {"Benificiary Name": ben_name,
            "Gender": gender,
            "Document Type": doc_type,
            "Document/AC Number": id_no,
            "Name of Bank": bank_name,
            "Type of Transaction": trn_type,
            "Sender Name":sender_name,
            "Sender Gender":sender_gender,
            "Sender Occupation":sender_occupation,
            "Source Country": source_country,
            "Name of Exchange House/Bank/IMTO": exchange_house,
            "Date of Sending Remittance(DD-MMM-YY)":date_sending_remittance,
            "Amount Remitted (in terms of Foreign Currency)": fc_amount,
            "Type of Foreign Currency": currency,
            "Exchange Rate": exchange_rate,
            "Amount Remitted (BDT)": bdt_amount,
            "Amount Remitted (USD)": usd_amount,
            "Amount of Incentive (BDT)": cash_incentive_amount,
            "Date of Payment of Incentive(DD-MMM-YY)": date_cashincentive_paid,
            "Comments": remarks,
            "Reference": reference,
            "Branch": branch,
            "Dealing Official": dealing_offical,
            "Cell Phone": dealing_cell,
            }
    df = pd.DataFrame(dct)
    return df




