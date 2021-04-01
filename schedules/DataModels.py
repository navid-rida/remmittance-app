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


def remittance_rit(qset):
    #Takes remittance quesryset and returns RIT Dataframe
    remit_df = qset_to_df(qset.filter(cash_incentive_status='P'))
    remit_df['date_create'] = pd.to_datetime(remit_df['date_create']).dt.date
    receiver_df = qset_to_df(Receiver.objects.filter(remmit__in=qset).distinct())
    e_df = qset_to_df(ExchangeHouse.objects.filter(remmit__in=qset).distinct())
    currency_qset = Currency.objects.filter(remmit__in=qset).distinct()
    rate_qset = Rate.objects.filter(currency__in=currency_qset)
    currency_df = qset_to_df(currency_qset)
    rate_df = qset_to_df(rate_qset)
    rate_df['date'] = pd.to_datetime(rate_df['date']).dt.date
    usd_df = qset_to_df(Rate.objects.filter(currency__short= 'USD'))
    country_df = qset_to_df(Country.objects.filter(remmit__in=qset).distinct())
    cashin_df = qset_to_df(CashIncentive.objects.filter(entry_category='P').filter(remittance__in=qset).distinct())

    df = pd.merge(receiver_df, remit_df, how = 'outer', left_on='id', right_on='receiver_id', suffixes=('_receiver', '_remittance'))
    df = df.merge(cashin_df, how = 'outer', left_on='id_remittance', right_on='remittance_id', suffixes=('', '_cashin'))
    df = df.merge(e_df, how = 'outer', left_on='exchange_id', right_on='id',suffixes=('', '_exchange'))
    df = df.merge(country_df, how = 'outer', left_on='rem_country_id', right_on='id',suffixes=('', '_country'))
    df = df.merge(currency_df, how = 'outer', left_on='currency_id', right_on='id', suffixes=('', '_currency'))
    df = df.merge(rate_df, how = 'left', left_on = ['id_currency','date_create'], right_on=['currency_id','date'], suffixes=('','_rate'))
    df = df.merge(usd_df, how = 'left', left_on = 'date_create', right_on='date', suffixes=('','_usd'))

    df['bank'] = 'NRB COMMERCIAL BANK LTD.'
    df['trn_type'] = 'CASH-PICKUP(OTC)'
    df['date_cash_incentive_paid_cashin'] = df['date_cash_incentive_paid_cashin'].dt.date
    #df['exc_rate'] = Decimal(80.24)
    df['amt_bdt'] = df.apply(lambda x: x['amount'] if x['short']=='BDT' else Decimal(x['amount'])*Decimal(x['rate']), axis=1)
    df['currency_short_name'] = df['short'].apply(lambda x: "USD" if x=='BDT' else x)
    df['receiver_gender'] = df['gender'].apply(gender_abbr)
    df['sender_gender'] = df['sender_gender'].apply(gender_abbr)
    df['amt_usd'] = df['amt_bdt']/df['rate_usd']
    df['amount'] = df.apply(lambda x:x['amt_usd'] if x['short']=='BDT' else x['amount'], axis=1)
    df['date_cash_incentive_paid_cashin'] = pd.to_datetime(df['date_cash_incentive_paid_cashin']).dt.strftime("%d-%b-%Y").str.upper()
    return df[['reference','name','receiver_gender','idtype','idno', 'bank','trn_type', 'sender', 'sender_gender','sender_occupation', 'name_country','name_exchange', 'date_sending', 'amount','currency_short_name', 'rate', 'amt_bdt','amt_usd','cash_incentive_amount_cashin', 'date_cash_incentive_paid_cashin']]

    """name= []
    for q in qset:
        name.append(q.receiver.name)
        receiver_gender.append(q.receiver.gender)
        doc_type.append(q.receiver.idtype)
        doc_no.append(q.receiver.idno)
        bankname.append('NRB COMMERCIAL BANK LTD.')
        tr_type.append(q.get_ci_trn_type())"""



