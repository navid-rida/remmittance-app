#from .models import Remmit,Branch,Booth,ExchangeHouse
#from rem.models import CashIncentive
import pandas as pd
from datetime import datetime, date,timedelta
import io
from django.db.models import IntegerField, F, Value
from .validators import *
from django.core.exceptions import ValidationError
#from rem.models import *
####################### fuzzywuzzy imports ##################################
from .search import remittance_search
from fuzzywuzzy import fuzz
from fuzzywuzzy import process


############################# Variables and Lists ######################################
gl = ['901130537010101','901130539010101','901130537010103','901130537010105','901130537010108', '901130537010110', '901130537010112', '901130537010118']
cd = ['33300000414','33300000616','33300000670','33300000741','33300000848', '902010301062901', '902010301062903', '010124100000006']
ac_list = gl + cd

####################### common functions#################################################

def excel_output(df):
    """ Takes DataFrame as input and returns excel file for download """
    output = io.BytesIO()
    #time = str(date.today())
    #filename = "output "+time+".xlsx"
    writer = pd.ExcelWriter(output, engine='xlsxwriter', options={'remove_timezone': True})
    #writer.book.filename = io
    df.to_excel(writer,'Sheet1', index=False, header=True)
    writer.save()
    xlsx_data = output.getvalue()
    return xlsx_data

def qset_to_df(qset, datatype='object'):
    """ accepts Django queryset and converts to pandas Dataframe """
    df = pd.DataFrame(list(qset.values()), dtype=datatype)
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
def make_ac_df(list,category,columns,payments):
    #day = date.strftime('%Y-%m-%d')
    dict = {}
    #payments = Payment.objects.filter(id__in=list).order_by('requestpay__remittance__exchange','dateresolved','requestpay__remittance__branch__code')
    #Sl= []
    tr_date = []
    br_code = []
    #booth_code = []
    #br_name= []
    ac_no = []
    type = []
    amount = []
    narrations = []
    flags = []
    amount_type = []
    #country = []
    i = 1
    for pay in payments:
        #Sl.append(i)
        #i = i + 1
        dr_cr = 'C' if category=='gl' else 'D'
        tr_date.append(date.today().strftime('%d/%m/%Y'))
        #br_code.append(rem.branch.code)
        if category=='gl':
            branch = pay.requestpay.remittance.booth.code if pay.requestpay.remittance.booth else pay.requestpay.remittance.branch.code
            br_code.append(branch)
            #booth = pay.requestpay.remittance.booth.code if pay.requestpay.remittance.booth else '0001'
            #booth_code.append(booth)
            ac_no.append(pay.requestpay.remittance.exchange.gl_no)
        else:
            br_code.append(pay.requestpay.remittance.exchange.ac_no_branch.code)
            #booth_code.append("0001")
            ac_no.append(pay.requestpay.remittance.exchange.ac_no)
        #br_name.append(pay.requestpay.remittance.branch.name)
        type.append(dr_cr)
        amount.append(pay.requestpay.remittance.amount)

        if dr_cr == 'C':
            br_sub_br = pay.requestpay.remittance.booth.code if pay.requestpay.remittance.booth else pay.requestpay.remittance.branch.code
            narration = "Adj for "+ pay.requestpay.remittance.exchange.name +" Cash payment at "+br_sub_br+" on "+pay.dateresolved.strftime('%d/%m/%Y')
        else:

            br_sub_br = pay.requestpay.remittance.booth.code if pay.requestpay.remittance.booth else pay.requestpay.remittance.branch.code
            narration = pay.requestpay.remittance.reference +" pmt fvg "+br_sub_br+" on "+pay.dateresolved.strftime('%d/%m/%Y')
        narrations.append(narration)
        if category =='gl':
            flag= 0
        else:
            flag= 0 if pay.requestpay.remittance.exchange.ac_no[0]=='9' else 1
        flags.append(flag)
        amount_type.append('000')
        #country.append(pay.requestpay.remittance.rem_country.name)
        dict ={
        #'Sl' : Sl,
        'date' : tr_date,
        'branch_code': br_code,
        #'booth_code': booth_code,
        #'branch_name': br_name,
        'ac_no' : ac_no,
        'type' : type,
        'amount' : amount,
        'narrations' : narrations,
        'flags' : flags,
        'amount_type': amount_type
        #'country' : country
        }
    df = pd.DataFrame(dict)
    df['ac_no'] = pd.Categorical(df['ac_no'], ordered= True)
    #df = df.sort_values(by=['ac_no','branch_code'])
    return df

def make_cash_incentive_df(list,category,columns,cis):
    #day = date.strftime('%Y-%m-%d')
    dict = {}
    #payments = Payment.objects.filter(id__in=list).order_by('requestpay__remittance__exchange','dateresolved','requestpay__remittance__branch__code')
    #Sl= []
    tr_date = []
    br_code = []
    #br_name= []
    #booth_code= []
    ac_no = []
    type = []
    amount = []
    narrations = []
    flags = []
    amount_type = []
    #country = []
    i = 1
    for ci in cis:
        #Sl.append(i)
        #i = i + 1
        dr_cr = 'C' if category=='gl' else 'D'
        tr_date.append(date.today().strftime('%d/%m/%Y'))
        #br_code.append(rem.branch.code)
        if category=='gl':
            branch = ci.remittance.booth.code if ci.remittance.booth else ci.remittance.branch.code
            br_code.append(branch)
            #booth = pay.requestpay.remittance.booth.code if pay.requestpay.remittance.booth else '0001'
            #booth_code.append(booth)
            ac_no.append(ci.remittance.exchange.cash_incentive_gl_no)
            #br_name.append(pay.requestpay.remittance.branch.name)
        else:
            br_code.append("0100")
            #booth_code.append('0001')
            ac_no.append("902010301063511")
            #br_name.append("Head Office")
        #br_name.append(pay.requestpay.remittance.branch.name)
        type.append(dr_cr)
        amount.append(ci.cash_incentive_amount)

        if dr_cr == 'C':
            br_sub_br = ci.remittance.booth.code if ci.remittance.booth else ci.remittance.branch.code
            narration = "Adj for Incentive against "+ ci.remittance.reference +" at "+br_sub_br+" on "+ci.date_cash_incentive_paid.strftime('%d/%m/%Y')
        else:
            br_sub_br = ci.remittance.booth.code if ci.remittance.booth else ci.remittance.branch.code
            narration = "Agt "+ ci.remittance.exchange.name+" Pmt "+ci.remittance.reference +" fvg "+br_sub_br+" on "+ci.date_cash_incentive_paid.strftime('%d/%m/%Y')
        narrations.append(narration)
        if category=='br_ac' and dr_cr == 'D':
            flag=0
        else:
            flag=0
        flags.append(flag)
        amount_type.append('000')
        #country.append(ci.remittance.rem_country.name)
        dict ={
        #'Sl' : Sl,
        'date' : tr_date,
        'branch_code': br_code,
        #'branch_name': br_name,
        #'booth_code': booth_code,
        'ac_no' : ac_no,
        'type' : type,
        'amount' : amount,
        'narrations' : narrations,
        'flags' : flags,
        'amount_type': amount_type
        #'country' : country
        }
    df = pd.DataFrame(dict)
    #df['ac_no'] = pd.Categorical(df['ac_no'], ac_list)
    #df = df.sort_values(by=['ac_no','branch_code'])
    return df

def rem_bb_summary(list, payments):
    payments = payments.filter(id__in=list)
    columns=['date', 'br_code', 'ac_no', 'type', 'amount', 'narration', 'flag']
    gl_df = make_ac_df(list,'gl',columns, payments)
    ac_df = make_ac_df(list,'br_ac',columns, payments)
    frames = [gl_df, ac_df]
    complete_df = pd.concat(frames)
    return complete_df

def cash_incentive_df(list, ci):
    ci = ci.filter(id__in=list)
    columns=['date', 'br_code', 'br_name','booth_code', 'ac_no', 'type', 'amount', 'narration', 'flag', 'country']
    gl_df = make_cash_incentive_df(list,'gl',columns, ci)
    ac_df = make_cash_incentive_df(list,'br_ac',columns, ci)
    frames = [gl_df, ac_df]
    complete_df = pd.concat(frames)
    return complete_df
################################# Claim Related Report ########################
def make_claim_df(claim_list, columns = ['Sl','Name of Bank','Name of Branch','A/C Number (15 digit)','A/C Title','Amount of Remittance in BDT','Date of A/C Credit','Remittance Received through BEFTN/RTGS','Name of Remittance Collecting/BEFTN Processing Bank','Date of Claim']):
    """ Accept Claim queryset and returns DatFrame"""
    sl=[]
    nrbc_bank = []
    branch = []
    ac_no = []
    ac_title = []
    amount=[]
    date_account_credit=[]
    channel = []
    other_bank=[]
    claim_date=[]
    i=1
    for claim in claim_list:
        sl.append(i)
        i=i+1
        nrbc_bank.append("NRBC Bank Ltd.")
        branch.append(claim.branch.name.upper())
        ac_no.append(claim.account_no)
        ac_title.append(claim.account_title)
        amount.append(claim.remittance_amount)
        date_account_credit.append(claim.date_account_credit)
        channel.append(claim.get_channel_display())
        other_bank.append(claim.collecting_bank.name)
        claim_date.append(claim.date_claim.date())
    dc = {
            'SL':sl,
            'Name of Bank':nrbc_bank,
            'Name of Branch': branch,
            'A/C Number': ac_no,
            'A/C Title': ac_title,
            'Amount of Remittance in BDT': amount,
            'Date of A/C Credit': date_account_credit,
            'Remittance Received Through BEFTN/RTGS': channel,
            'Name of Remittance Processing Bank': other_bank,
            'Date of Claim': claim_date
    }
    df = pd.DataFrame(dc)
    return df.sort_values(by=['Name of Remittance Processing Bank',])
################################## name search related functions ##################################
def name_search(search_text, db_txt):
    if fuzz.token_set_ratio(search_text,db_text) > 70:
        return True

def name_search_result(qset, search_text):
    #qset = qset.annotate(score=Value(0,IntegerField()))
    df = qset_to_df(qset)
    #df['score'] = df['name'].apply(lambda x: fuzz.partial_ratio(search_text,x))
    df['score'] = df['name'].apply(lambda x: max(fuzz.partial_ratio(search_text,x),fuzz.token_sort_ratio(search_text,x)))
    pass



############################ helper functions #########################################

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def get_branch_from_ip(ip):
    code = '0'+ip.split('.')[2]
    branch = Branch.objects.get(code=code)
    return branch

################################# Remittance list Search ########################################
def filter_remittance(query_set, start_date=None, end_date= None, branch= None, booth= None, exchange_house=None, cash_incentive_status=None, cash_incentive_settlement_done=None,keyword=None, BranchBooth=None):
    r = query_set
    if start_date and end_date:
        r = r.filter(date_create__date__range=(start_date,end_date))
    if branch:
        r = r.filter(branch=branch)
    if booth:
        r = r.filter(booth=booth)
    if exchange_house:
        r = r.filter(exchange=exchange_house)
    if keyword:
        r=remittance_search(keyword,r)
    if cash_incentive_status:
        r = r.filter(cash_incentive_status=cash_incentive_status)
    if cash_incentive_settlement_done==True:
        r = r.filter(date_cash_incentive_settlement__isnull=False)
    if BranchBooth=='branch':
        r = r.filter(booth=None)
    if BranchBooth=='booth':
        r = r.filter(booth__isnull=False)
    return r.order_by('exchange','-date_create','branch__code')

def filter_claim(query_set, start_date=None, end_date= None, branch= None, booth=None):
    claims = query_set
    if start_date and end_date:
        claims = claims.filter(date_claim__date__range=(start_date,end_date))
    if branch:
        claims = claims.filter(branch=branch)
    if booth:
        claims = claims.filter(booth=booth)
    return claims.order_by('-date_claim','branch__code')


def get_reference_no_from_narration(narration,validatorlist=[validate_western_code,validate_ria,validate_placid, validate_xpress,validate_moneygram, validate_prabhu_ref, validate_merchantrade_ref, validate_necmoney_ref, validate_necitaly_ref, validate_cbl_ref, swift_re]):
    """gets all reference number from a narration. returns list"""
    ref_list = []
    for e in narration.split():
        for fn in validatorlist:
            try:
                fn(e)
                if e not in ref_list:
                    ref_list.append(e)
            except ValidationError:
                pass
    return ref_list

def get_reference_no_list_from_df(df):
    ref_list= []
    for index,row in df.iterrows():
        lst = get_reference_no_from_narration(row['narrations'])
        ref_list=ref_list+lst
    return ref_list


############################################## view specific functions ##################################################

def clean_settlement_df(df):
    df['nc'] = df.isna().any(axis=1)
    return list(df[df['nc']==True].index) if len(list(df[df['nc']==True].index)) else None
