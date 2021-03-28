from rem.models import Remmit,Receiver, CashIncentive, ExchangeHouse, Country
from .models import *
import pandas as pd
from datetime import datetime, date,timedelta
import io
from django.db.models import IntegerField, F, Value
#from .validators import *
from django.core.exceptions import ValidationError
#from rem.models import *
from rem.DataModels import qset_to_df
from decimal import Decimal
####################### fuzzywuzzy imports ##################################
#from .search import remittance_search
from fuzzywuzzy import fuzz
from fuzzywuzzy import process






def remittane_rit(qset):
    #Takes remittance quesryset and returns RIT Dataframe
    remit_df = qset_to_df(qset)
    receiver_df = qset_to_df(Receiver.objects.filter(remmit__in=qset).distinct())
    e_df = qset_to_df(ExchangeHouse.objects.filter(remmit__in=qset).distinct())
    currency_df = qset_to_df(Currency.objects.filter(remmit__in=qset).distinct())
    country_df = qset_to_df(Country.objects.filter(remmit__in=qset).distinct())
    cashin_df = qset_to_df(CashIncentive.objects.filter(entry_category='P',remittance__in=qset).distinct())
    df = pd.merge(receiver_df, remit_df, how = 'outer', left_on='id', right_on='receiver_id', suffixes=('_receiver', '_remittance'))
    df = df.merge(cashin_df, how = 'outer', left_on='id_remittance', right_on='remittance_id', suffixes=('', '_cashin'))
    df = df.merge(e_df, how = 'outer', left_on='exchange_id', right_on='id',suffixes=('', '_exchange'))
    df = df.merge(country_df, how = 'outer', left_on='rem_country_id', right_on='id',suffixes=('', '_country'))
    df = df.merge(currency_df, how = 'outer', left_on='currency_id', right_on='id', suffixes=('', '_currency'))
    df['bank'] = 'NRB COMMERCIAL BANK LTD.'
    df['trn_type'] = 'CASH-PICKUP(OTC)'
    df['exc_rate'] = Decimal(80.24)
    df['amt_bdt'] = df['amount']*df['exc_rate']
    return df#[['name_main','gender','idtype','idno', 'bank','trn_type', 'sender', 'sender_gender','sender_occupation', 'name_country','name_exchange', 'date_sending', 'amount','short', 'exc_rate', 'amt_bdt', 'cash_incentive_amount_ci', 'date_cash_incentive_paid_ci']]

    """name= []
    for q in qset:
        name.append(q.receiver.name)
        receiver_gender.append(q.receiver.gender)
        doc_type.append(q.receiver.idtype)
        doc_no.append(q.receiver.idno)
        bankname.append('NRB COMMERCIAL BANK LTD.')
        tr_type.append(q.get_ci_trn_type())"""
