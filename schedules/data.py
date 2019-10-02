import pandas as pd
import numpy as np
from pathlib import Path
import datetime

###################### paths ###########################################
folder_path = 'F:\\Projects\\Return RIT\\Return RIT_August 2019'
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


############################ Reference path and DFs #########################################################
ref_file_path = Path('F:\\Projects\\Return RIT\\REFERENCE_FILE.xlsm')
ref_ad_fi_branch = pd.read_excel(ref_file_path, sheet_name='AD_TO_BR', dtype= {'FI_BR_CODE':object,} )
ref_currency = pd.read_excel(ref_file_path, sheet_name='CURRENCY')
ref_country = pd.read_excel(ref_file_path, sheet_name='COUNTRY', )
ref_commodity = pd.read_excel(ref_file_path, sheet_name='BOP_COMMODITY', dtype= {'COMMODITY_ID':str,})
ref_commodity['HS_CODE'] = ref_commodity['COMMODITY_ID'].str[-8:].apply(int)
ref_unit = pd.read_excel(ref_file_path, sheet_name='UOM')
ref_fx_type_df = pd.read_excel(ref_file_path, sheet_name='FX_TYPE', dtype = float)
ref_economic_sector_df = pd.read_excel(ref_file_path, sheet_name='CATEGORY_TO_ECONOMIC_SECTOR',)

def get_fx_trn_type(value,ref_fx_type_df):
    #types = ref_fx_type_df.to_dict(orient='list')
    for col in ref_fx_type_df.columns:
        if value in list(ref_fx_type_df[col].values):
            return col
    return None

#################################### Export Part #########################################
exp_columns = ['Schedule','Type','Month','AD','CUR_CODE','Serial','UNIT_CODE','Volume','fc_amount','COUNTRY_CODE','HS_CODE']
exp_df = pd.read_csv(export_text_path,sep='|', names=exp_columns, )


def get_exp_rit_df(df):
    #df = exp_df
    df['DATED'] = datetime.datetime.today().strftime("%d-%b-%Y")
    df['FI_NAME'] = "NRB COMMERCIAL BANK LTD."
    df['SERIAL_NO'] = np.arange(1,len(df)+1)
    df = df.merge(ref_ad_fi_branch, how='left', left_on='AD',right_on='AD_CODE')
    df = df.merge(ref_currency, how='left')
    df = df.merge(ref_country, how='left',)
    df = df.merge(ref_commodity, how='left',)
    df = df.merge(ref_unit, how='left',)
    df['REPORT_TYPE'] = df['Schedule'].apply(get_fx_trn_type,args=[ref_fx_type_df])
    new_df = df[['DATED','FI_NAME','SERIAL_NO','FI_BR_CODE','REPORT_TYPE','CURRENCY','Schedule','Type','COUNTRY','COMMODITY_ID','UNIT_MEASURE','fc_amount','Volume']]
    return new_df

########################################## Import Payment #################################################
imp_pay_columns = ['Schedule','Type','Month','AD','CUR_CODE','Serial','UNIT_CODE','Volume','fc_amount','COUNTRY_CODE','HS_CODE','CATEGORY_CODE']
imp_pay_df = pd.read_csv(import_payment_text_path,sep='|', names=imp_pay_columns,)

def get_imp_pay_rit_df(df):
    #df = exp_df
    df['DATED'] = datetime.datetime.today().strftime("%d-%b-%Y")
    df['FI_NAME'] = "NRB COMMERCIAL BANK LTD."
    df['SERIAL_NO'] = np.arange(1,len(df)+1)
    df = df.merge(ref_ad_fi_branch, how='left', left_on='AD',right_on='AD_CODE')
    df = df.merge(ref_currency, how='left')
    df = df.merge(ref_country, how='left',)
    df = df.merge(ref_commodity, how='left',)
    df = df.merge(ref_unit, how='left',)
    df = df.merge(ref_economic_sector_df, how='left',)
    df['REPORT_TYPE'] = df['Schedule'].apply(get_fx_trn_type,args=[ref_fx_type_df])
    new_df = df[['DATED','FI_NAME','SERIAL_NO','FI_BR_CODE','REPORT_TYPE','CURRENCY','Schedule','Type','COUNTRY','COMMODITY_ID','UNIT_MEASURE','fc_amount','Volume','Economic Sector_Code']]
    return new_df

####################################### Invisible Payments ########################################################

invisible_pay_columns = ['Schedule','Type','Month','AD','CUR_CODE','Serial','fc_amount','COUNTRY_CODE','PURPOSE_CODE','CATEGORY_CODE']
invisible_pay_df = pd.read_csv(invisible_payment_text_path,sep='|', names=invisible_pay_columns, dtype= {'PURPOSE_CODE':str,})

def get_inv_pay_rit_df(df):
    #df = exp_df
    df['DATED'] = datetime.datetime.today().strftime("%d-%b-%Y")
    df['FI_NAME'] = "NRB COMMERCIAL BANK LTD."
    df['SERIAL_NO'] = np.arange(1,len(df)+1)
    df = df.merge(ref_ad_fi_branch, how='left', left_on='AD',right_on='AD_CODE')
    df = df.merge(ref_currency, how='left')
    df = df.merge(ref_country, how='left',)
    #df = df.merge(ref_commodity, how='left',)
    #df = df.merge(ref_unit, how='left',)
    df = df.merge(ref_economic_sector_df, how='left',)
    df['REPORT_TYPE'] = df['Schedule'].apply(get_fx_trn_type,args=[ref_fx_type_df])
    new_df = df[['DATED','FI_NAME','SERIAL_NO','FI_BR_CODE','REPORT_TYPE','CURRENCY','Schedule','Type','COUNTRY','fc_amount','PURPOSE_CODE','Economic Sector_Code']]
    return new_df

############################################## Invisible Receipts #####################################################################

invisible_rec_columns = ['Schedule','Type','Month','AD','CUR_CODE','Serial','fc_amount','COUNTRY_CODE','PURPOSE_CODE']
invisible_rec_df = pd.read_csv(invisible_receipt_text_path,sep='|', names=invisible_rec_columns, dtype= {'PURPOSE_CODE':str,})

def get_inv_rec_rit_df(df):
    #df = exp_df
    df['DATED'] = datetime.datetime.today().strftime("%d-%b-%Y")
    df['FI_NAME'] = "NRB COMMERCIAL BANK LTD."
    df['SERIAL_NO'] = np.arange(1,len(df)+1)
    df = df.merge(ref_ad_fi_branch, how='left', left_on='AD',right_on='AD_CODE')
    df = df.merge(ref_currency, how='left')
    df = df.merge(ref_country, how='left',)
    #df = df.merge(ref_commodity, how='left',)
    #df = df.merge(ref_unit, how='left',)
    df['REPORT_TYPE'] = df['Schedule'].apply(get_fx_trn_type,args=[ref_fx_type_df])
    new_df = df[['DATED','FI_NAME','SERIAL_NO','FI_BR_CODE','REPORT_TYPE','CURRENCY','Schedule','Type','COUNTRY','fc_amount','PURPOSE_CODE']]
    return new_df

###################################################### Wage Remiitance ############################################
wage_remit_columns = ['Schedule','Type','Month','AD','CUR_CODE','Serial','COUNTRY_CODE','fc_amount',]
wage_remit_df = pd.read_csv(wage_remit_text_path,sep='|', names=wage_remit_columns, )

def get_wage_remit_rit_df(df):
    #df = exp_df
    df['DATED'] = datetime.datetime.today().strftime("%d-%b-%Y")
    df['FI_NAME'] = "NRB COMMERCIAL BANK LTD."
    df['SERIAL_NO'] = np.arange(1,len(df)+1)
    df = df.merge(ref_ad_fi_branch, how='left', left_on='AD',right_on='AD_CODE')
    df = df.merge(ref_currency, how='left')
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


final_df = rit_all_df(exp_df,imp_pay_df,invisible_pay_df,invisible_rec_df,wage_remit_df)
