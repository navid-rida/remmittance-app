import pandas as pd
#from pandas.core.arrays.sparse import dtype
import numpy as np
from pathlib import Path
import datetime

###################### paths ###########################################
"""folder_path = "F:\\Projects\\Return RIT\\2022\\RIT-MARCH-2022"
export_text_file = 'exprecpt.txt'
import_payment_text_file = 'imppaynt.txt'
invisible_payment_text_file = 'invpaynt.txt'
invisible_receipt_text_file = 'invrecpt.txt'
wage_remit_text_file = 'wagremit.txt'
export_text_path = Path(folder_path,export_text_file)
import_payment_text_path = Path(folder_path,import_payment_text_file)
invisible_payment_text_path = Path(folder_path,invisible_payment_text_file)
invisible_receipt_text_path = Path(folder_path,invisible_receipt_text_file)
wage_remit_text_path = Path(folder_path,wage_remit_text_file)

####################################### Reference file functions #######################################
def get_currency_df():
    pass

############################ Reference path and DFs #########################################################
ref_file_path = Path('REFERENCE_FILE_new.xlsm')
ref_additional_data_path = Path('ref_additional_data.xlsx')
zero_matrix_path = Path('zero matrix_August 2021.xls')

ref_ad_fi_branch = pd.read_excel(ref_additional_data_path, sheet_name='AD_TO_BR', dtype={'FI_BR_CODE': str})

zero_currency = pd.read_excel(zero_matrix_path,sheet_name='CURRCODE', skiprows=2,names=['CCY_ID','CUR_CODE'])
ref_currency = pd.read_excel(ref_file_path, sheet_name='CURRENCY')
ref_currency = ref_currency.merge(zero_currency, how='left', on='CCY_ID')

zero_country = pd.read_excel(zero_matrix_path,sheet_name='Country', names=['COUNTRY_ID', 'COUNTRY_CODE'], dtype={'COUNTRY_CODE': str})
ref_country = pd.read_excel(ref_file_path, sheet_name='COUNTRY')
ref_country = ref_country.merge(zero_country, how='left', on='COUNTRY_ID')
ref_country['COUNTRY_CODE'] = ref_country['COUNTRY_CODE'].apply(str)
ref_country['COUNTRY_CODE'] = ref_country['COUNTRY_CODE'].str.zfill(4)
#ref_country = ref_country[ref_country['COUNTRY_CODE']!='DEFAULT']


ref_commodity = pd.read_excel(ref_file_path, sheet_name='BOP_COMMODITY', dtype= {'COMMODITY_ID':str,})
ref_commodity['HS_CODE'] = ref_commodity['COMMODITY_ID'].str[-8:]#.apply(int)

zero_unit = pd.read_excel(zero_matrix_path,sheet_name='UNITCODE', skiprows=1, dtype=object, names=['CODE_VALUE','UNIT_CODE','UNIT_NAME'])
ref_unit = pd.read_excel(ref_file_path, sheet_name='UOM', dtype=object)
ref_unit = ref_unit.merge(zero_unit, how='left', on='CODE_VALUE')
ref_unit['UNIT_CODE'] = ref_unit['UNIT_CODE'].apply(str)

ref_fx_type_df = pd.read_excel(ref_additional_data_path, sheet_name='FX_TYPE', dtype = float)

ref_economic_sector_df = pd.read_excel(ref_additional_data_path, sheet_name='CATEGORY_TO_ECONOMIC_SECTOR', dtype=str)

def get_fx_trn_type(value,ref_fx_type_df):
    #types = ref_fx_type_df.to_dict(orient='list')
    for col in ref_fx_type_df.columns:
        if value in list(ref_fx_type_df[col].values):
            return col
    return None

#################################### Export Part #########################################
exp_columns = ['Schedule','Type','Month','AD','CUR_CODE','Serial','UNIT_CODE','Volume','fc_amount','COUNTRY_CODE','HS_CODE']
exp_df = pd.read_csv(export_text_path,sep='|', names=exp_columns, dtype={'COUNTRY_CODE':str, 'HS_CODE':object, 'UNIT_CODE': object})


def get_exp_rit_df(df):
    #df = exp_df
    df['DATED'] = datetime.datetime.today().strftime("%d-%b-%Y")
    df['FI_NAME'] = "NRB COMMERCIAL BANK LTD."
    df['SERIAL_NO'] = np.arange(1,len(df)+1)
    df = df.merge(ref_ad_fi_branch, how='left', left_on='AD',right_on='AD_CODE')
    df = df.merge(ref_currency, how='left')
    df['COUNTRY_CODE'] = df['COUNTRY_CODE'].apply(str)
    df = df.merge(ref_country, how='left', on='COUNTRY_CODE')
    df = df.merge(ref_commodity, how='left',)
    df['UNIT_CODE'] = df['UNIT_CODE'].apply(str)
    df = df.merge(ref_unit, how='left',)
    df['REPORT_TYPE'] = df['Schedule'].apply(get_fx_trn_type,args=[ref_fx_type_df])
    new_df = df[['DATED','FI_NAME','SERIAL_NO','FI_BR_CODE','REPORT_TYPE','CURRENCY','Schedule','Type','COUNTRY','COMMODITY_ID','UNIT_MEASURE','fc_amount','Volume']]
    return new_df

########################################## Import Payment #################################################
imp_pay_columns = ['Schedule','Type','Month','AD','CUR_CODE','Serial','UNIT_CODE','Volume','fc_amount','COUNTRY_CODE','HS_CODE','CATEGORY_CODE']
imp_pay_df = pd.read_csv(import_payment_text_path,sep='|', names=imp_pay_columns, dtype={'COUNTRY_CODE':str, 'HS_CODE':object, 'UNIT_CODE': object,'CATEGORY_CODE':object})

def get_imp_pay_rit_df(df):
    #df = exp_df
    df['DATED'] = datetime.datetime.today().strftime("%d-%b-%Y")
    df['FI_NAME'] = "NRB COMMERCIAL BANK LTD."
    df['SERIAL_NO'] = np.arange(1,len(df)+1)
    df = df.merge(ref_ad_fi_branch, how='left', left_on='AD',right_on='AD_CODE')
    df = df.merge(ref_currency, how='left')
    df['COUNTRY_CODE'] = df['COUNTRY_CODE'].apply(str)
    df = df.merge(ref_country, how='left',)
    df = df.merge(ref_commodity, how='left',)
    df['UNIT_CODE'] = df['UNIT_CODE'].apply(str)
    df = df.merge(ref_unit, how='left',)
    df = df.merge(ref_economic_sector_df, how='left',)
    df['REPORT_TYPE'] = df['Schedule'].apply(get_fx_trn_type,args=[ref_fx_type_df])
    new_df = df[['DATED','FI_NAME','SERIAL_NO','FI_BR_CODE','REPORT_TYPE','CURRENCY','Schedule','Type','COUNTRY','COMMODITY_ID','UNIT_MEASURE','fc_amount','Volume','Economic Sector_Code']]
    return new_df

####################################### Invisible Payments ########################################################

invisible_pay_columns = ['Schedule','Type','Month','AD','CUR_CODE','Serial','fc_amount','COUNTRY_CODE','PURPOSE_CODE','CATEGORY_CODE']
invisible_pay_df = pd.read_csv(invisible_payment_text_path,sep='|', names=invisible_pay_columns, dtype={'PURPOSE_CODE':str, 'COUNTRY_CODE':str, 'HS_CODE':object, 'UNIT_CODE': object,'CATEGORY_CODE':object,})

def get_inv_pay_rit_df(df):
    #df = exp_df
    df['DATED'] = datetime.datetime.today().strftime("%d-%b-%Y")
    df['FI_NAME'] = "NRB COMMERCIAL BANK LTD."
    df['SERIAL_NO'] = np.arange(1,len(df)+1)
    df = df.merge(ref_ad_fi_branch, how='left', left_on='AD',right_on='AD_CODE')
    df = df.merge(ref_currency, how='left')
    df['COUNTRY_CODE'] = df['COUNTRY_CODE'].apply(str)
    df = df.merge(ref_country, how='left',)
    #df = df.merge(ref_commodity, how='left',)
    #df = df.merge(ref_unit, how='left',)
    df = df.merge(ref_economic_sector_df, how='left',)
    df['REPORT_TYPE'] = df['Schedule'].apply(get_fx_trn_type,args=[ref_fx_type_df])
    new_df = df[['DATED','FI_NAME','SERIAL_NO','FI_BR_CODE','REPORT_TYPE','CURRENCY','Schedule','Type','COUNTRY','fc_amount','PURPOSE_CODE','Economic Sector_Code']]
    return new_df

############################################## Invisible Receipts #####################################################################

invisible_rec_columns = ['Schedule','Type','Month','AD','CUR_CODE','Serial','fc_amount','COUNTRY_CODE','PURPOSE_CODE']
invisible_rec_df = pd.read_csv(invisible_receipt_text_path,sep='|', names=invisible_rec_columns, dtype={'PURPOSE_CODE':str, 'COUNTRY_CODE':str, 'HS_CODE':object, 'UNIT_CODE': object,'CATEGORY_CODE':object,})

def get_inv_rec_rit_df(df):
    #df = exp_df
    df['DATED'] = datetime.datetime.today().strftime("%d-%b-%Y")
    df['FI_NAME'] = "NRB COMMERCIAL BANK LTD."
    df['SERIAL_NO'] = np.arange(1,len(df)+1)
    df = df.merge(ref_ad_fi_branch, how='left', left_on='AD',right_on='AD_CODE')
    df = df.merge(ref_currency, how='left')
    df['COUNTRY_CODE'] = df['COUNTRY_CODE'].apply(str)
    df = df.merge(ref_country, how='left',)
    #df = df.merge(ref_commodity, how='left',)
    #df = df.merge(ref_unit, how='left',)
    df['REPORT_TYPE'] = df['Schedule'].apply(get_fx_trn_type,args=[ref_fx_type_df])
    new_df = df[['DATED','FI_NAME','SERIAL_NO','FI_BR_CODE','REPORT_TYPE','CURRENCY','Schedule','Type','COUNTRY','fc_amount','PURPOSE_CODE']]
    return new_df

###################################################### Wage Remiitance ############################################
wage_remit_columns = ['Schedule','Type','Month','AD','CUR_CODE','Serial','COUNTRY_CODE','fc_amount',]
wage_remit_df = pd.read_csv(wage_remit_text_path,sep='|', names=wage_remit_columns, dtype={'COUNTRY_CODE':str, 'HS_CODE':object, 'UNIT_CODE': object,'CATEGORY_CODE':object})

def get_wage_remit_rit_df(df):
    #df = exp_df
    df['DATED'] = datetime.datetime.today().strftime("%d-%b-%Y")
    df['FI_NAME'] = "NRB COMMERCIAL BANK LTD."
    df['SERIAL_NO'] = np.arange(1,len(df)+1)
    df = df.merge(ref_ad_fi_branch, how='left', left_on='AD',right_on='AD_CODE')
    df = df.merge(ref_currency, how='left')
    df['COUNTRY_CODE'] = df['COUNTRY_CODE'].apply(str)
    df = df.merge(ref_country, how='left',)
    #df = df.merge(ref_commodity, how='left',)
    #df = df.merge(ref_unit, how='left',)
    df['REPORT_TYPE'] = df['Schedule'].apply(get_fx_trn_type,args=[ref_fx_type_df])
    new_df = df[['DATED','FI_NAME','SERIAL_NO','FI_BR_CODE','REPORT_TYPE','CURRENCY','Schedule','Type','COUNTRY','fc_amount',]]
    return new_df

###################################################### Other Functions ############################################

def rit_all_df(exp_rec,imp_pay,inv_pay,inv_rec,wage_remit):
    exp_rit_df = get_exp_rit_df(exp_rec)
    imp_pay_rit_df = get_imp_pay_rit_df(imp_pay)
    inv_rec_rit_df = get_inv_rec_rit_df(inv_rec)
    inv_pay_rit_df = get_inv_pay_rit_df(inv_pay)
    wage_remit_rit_df = get_wage_remit_rit_df(wage_remit)
    frames = [exp_rit_df, imp_pay_rit_df, inv_pay_rit_df, inv_rec_rit_df,wage_remit_rit_df]
    df = pd.concat(frames, sort=False)
    df['SERIAL_NO'] = np.arange(1,len(df)+1)
    return df


final_df = rit_all_df(exp_df,imp_pay_df,invisible_pay_df,invisible_rec_df,wage_remit_df)"""


########################################### Remittance Reports from DB ########################################

def get_daily_bb_remittance(qset):
    date=[]
    fi_name=[]
    sl=[]
    ad_fi_br=[]
    report_type=[]
    schedule_code=[]
    type_code=[]
    purpose_code=[]
    currency=[]
    country=[]
    district=[]
    nid=[]
    passport=[]
    amt_fcy=[]
    ref=[]
    exchange=[]
    branch=[]
    i=1
    for r in qset:
        date.append(r.dateresolved.date())
        fi_name.append("NRB COMMERCIAL BANK LTD.")
        sl.append(str(i))
        i=i+1
        ad_fi_br.append(r.requestpay.remittance.branch.ad_fi_code if not r.requestpay.remittance.is_thirdparty_remittance() else "0102")
        report_type.append("WAGE REMITTANCE")
        schedule_code.append(r.requestpay.remittance.get_schedule_code())
        type_code.append("4")
        purpose_code.append("")
        currency.append("USD" if r.requestpay.remittance.is_thirdparty_remittance() else r.requestpay.remittance.currency.short )
        country.append(r.requestpay.remittance.rem_country)
        district.append(r.requestpay.remittance.branch.district.name)
        nid.append(r.requestpay.remittance.receiver.get_nid())
        passport.append(r.requestpay.remittance.receiver.get_passport_no())
        amt_fcy.append(r.requestpay.remittance.get_fc_amount())
        ref.append(r.requestpay.remittance.reference)
        exchange.append(r.requestpay.remittance.exchange)
        branch.append(r.requestpay.remittance.branch.name)
    dct = {"DATED": date,
            "FI NAME": fi_name,
            "SERIAL NO": sl,
            "AD FI BRANCH": ad_fi_br,
            "REPORT TYPE": report_type,
            "SCHEDULE CODE": schedule_code,
            "TYPE CODE":type_code,
            "PURPOSE CODE":purpose_code,
            "CURRENCY":currency,
            "COUNTRY": country,
            "District": district,
            "NID": nid,
            "PASSPORT":passport,
            "AMOUNT FCY": amt_fcy,
            "Reference": ref,
            "Exchange": exchange,
            "Branch": branch,
            }
    df = pd.DataFrame(dct)
    return df
