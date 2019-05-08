from .models import *
import pandas as pd
from datetime import datetime, date,timedelta
import io
from django.db.models import IntegerField, F, Value
####################### fuzzywuzzy imports ##################################
from fuzzywuzzy import fuzz
from fuzzywuzzy import process


############################# Variables and Lists ######################################
gl = ['901130537010101','901130539010101','901130537010103','901130537010105','901130537010108']
cd = ['33300000414','33300000616','33300000670','33300000741','33300000848']
ac_list = gl + cd

####################### common functions#################################################

def excel_output(df):
    """ Takes DataFrame as input and returns excel file for download """
    output = io.BytesIO()
    #time = str(date.today())
    #filename = "output "+time+".xlsx"
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    #writer.book.filename = io
    df.to_excel(writer,'Sheet1', index=False, header=False)
    writer.save()
    xlsx_data = output.getvalue()
    return xlsx_data

def qset_to_df(qset):
    """ accepts Django queryset and converts to pandas Dataframe """
    df = pd.DataFrame(list(qset.values()))
    return df

def find_same_amount(df):
    """This function takes remmittance details dataframe as input
    and returns a modified dataframe marking the entries which has
    same exchange house AND Branch AND same amount"""
    ids = list(df['id'][df.duplicated(['amount','branch_id','exchange_id'],keep= False)==True].values)
    return ids

def search(date_from=None,date_to=None,exchange=None,branch=None,status=None):
    if status==None:
        rem_list = Remmit.objects.all()
    else:
        rem_list = Remmit.objects.filter(status=status)
    if date_from != None and date_to != None:
        rem_list = rem_list.filter(date_create__date__range=(date_from,date_to))
    if branch != None:
        rem_list = rem_list.filter(branch=branch)
    if exchange != None:
        rem_list = rem_list.filter(exchange=exchange)
    rem_list = rem_list.order_by('exchange', '-date')
    return rem_list

####################### Report Sepcific Functions #################################################
def make_ac_df(list,category,columns):
    #day = date.strftime('%Y-%m-%d')
    dict = {}
    payments = Payment.objects.filter(id__in=list).order_by('requestpay__remittance__exchange','requestpay__remittance__branch__code','-dateresolved')
    #Sl= []
    tr_date = []
    br_code = []
    br_name= []
    ac_no = []
    type = []
    amount = []
    narrations = []
    flags = []
    i = 1
    for pay in payments:
        #Sl.append(i)
        #i = i + 1
        dr_cr = 'C' if category=='gl' else 'D'
        tr_date.append(date.today().strftime('%d/%m/%Y'))
        #br_code.append(rem.branch.code)
        if category=='gl':
            br_code.append(pay.requestpay.remittance.branch.code)
            ac_no.append(pay.requestpay.remittance.exchange.gl_no)
        else:
            br_code.append("0101")
            ac_no.append(pay.requestpay.remittance.exchange.ac_no)
        br_name.append(pay.requestpay.remittance.branch.name)
        type.append(dr_cr)
        amount.append(pay.requestpay.remittance.amount)
        if dr_cr == 'C':
            narration = "Adj for "+ pay.requestpay.remittance.exchange.name +" Cash payment on "+pay.dateresolved.strftime('%d/%m/%Y')
        else:
            narration = pay.requestpay.remittance.reference +" pmt fvg "+pay.requestpay.remittance.branch.code+" on "+pay.dateresolved.strftime('%d/%m/%Y')
        narrations.append(narration)
        if category=='br_ac' and dr_cr == 'D':
            flag=1
        else:
            flag=0
        flags.append(flag)
        dict ={
        #'Sl' : Sl,
        'date' : tr_date,
        'branch_code': br_code,
        'branch_name': br_name,
        'ac_no' : ac_no,
        'type' : type,
        'amount' : amount,
        'narrations' : narrations,
        'flags' : flags
        }
    df = pd.DataFrame(dict)
    df['ac_no'] = pd.Categorical(df['ac_no'], ac_list)
    #df = df.sort_values(by=['ac_no','branch_code'])
    return df

def rem_bb_summary(list):
    columns=['date', 'br_code', 'br_name', 'ac_no', 'type', 'amount', 'narration', 'flag']
    gl_df = make_ac_df(list,'gl',columns)
    ac_df = make_ac_df(list,'br_ac',columns)
    frames = [gl_df, ac_df]
    complete_df = pd.concat(frames)
    return complete_df

################################## name search related functions ##################################
def name_search(search_text, db_txt):
    if fuzz.token_set_ratio(search_text,db_text) > 70:
        return True

def name_search_result(qset, search_text):
    #qset = qset.annotate(score=Value(0,IntegerField()))
    df = qset_to_df(qset)
    #df['score'] = df['name'].apply(lambda x: fuzz.partial_ratio(search_text,x))
    df['score'] = df['name'].apply(lambda x: max(fuzz.partial_ratio(search_text,x),fuzz.token_sort_ratio(search_text,x)))



############################ helper functions #########################################

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
