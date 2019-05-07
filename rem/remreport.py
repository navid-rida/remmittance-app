#from .models import *
import pandas as pd
from datetime import date
import io
import os
from pathlib import Path, WindowsPath
from .models import ExchangeHouse, Branch
from .DataModels import qset_to_df



def check_ext(file,ext):
    complete_extention = "."+ext
    if file.lower().endswith(complete_extention):
        return True

def get_file_list(path='.',ext='.csv'):
    p = Path(path)
    files = []
    for dir in p.iterdir():
        if not dir.is_dir():
            file_ext = dir.suffixes[len(dir.suffixes)-1]
            if file_ext == ext:
                files.append(dir.resolve())
    return files

def merge_xl(xllist):
    df_all = pd.DataFrame()
    for file in xllist:
        #df_single_file = pd.read_excel(file,header=None, names=['date','br_code','gl_key','dc','amount','narration','flag'])
        df_single_file = pd.read_excel(file,header=None, names=['date','br_code','gl_key','dc','amount','narration','flag'])
        df_all = df_all.append(df_single_file)
    final_df = df_all[df_all['dc']=='C']
    return final_df

def merge_csv(csvlist):
    df_all = pd.DataFrame()
    for file in csvlist:
        #df_single_file = pd.read_excel(file,header=None, names=['date','br_code','gl_key','dc','amount','narration','flag'])
        df_single_file = pd.read_csv(file,skiprows=[0,]).dropna(how='all')
        df_all = df_all.append(df_single_file)
        #df_all = df_all.drop("Unnamed: 14", axis=1)
    #final_df = df_all
    #final_df = final_df.drop("Unnamed: 14", axis=1)
    return df_all

#Unnamed: 14
def hellopops(path='.',ext='.csv'):
    xllist= get_file_list(path,ext)
    df = merge_xl(xllist)
    return df

def month_summary(path='.',ext='.csv'):
    batch_df = hellopops(path, ext)
    batch_df['gl_key'] = batch_df['gl_key'].apply(str)
    batch_df['br_code'] = "0"+batch_df['br_code'].apply(str)
    branch_df = qset_to_df(Branch.objects.all())
    exc_df = qset_to_df(ExchangeHouse.objects.all())
    df = pd.merge(batch_df,branch_df,how='outer', left_on='br_code', right_on='code')
    df = pd.merge(df,exc_df,how='outer', left_on='gl_key', right_on='gl_no')
    return df



######################### Ria Specific Wrangling Functions ########################################

def branch_from_ria_user(ria_user):
    branch_long = ria_user[5:].split()
    branch_list = branch_long if branch_long[-1] != 'Branch' else branch_long[0:-1]
    branch = "".join(branch_list)
    return branch

def ria_excel_to_df(path='.', excelfileobject=None):
    if excelfileobject != None:
        pass
    else:
        p = WindowsPath(path)
        df = pd.read_excel(p, skiprows=[0,1,2,3,5,]).dropna(how='any')
        return df

batch_columns=['date','br_code','acc','cd','amount','narration','flag']

def get_gl_batch_transaction(df,batch_columns,name='RIA MONEY TRANSFER'):
    gl_df = pd.DataFrame(columns=batch_columns)
    exc = ExchangeHouse.objects.get(name=name)
    df['narration'] = 'Adj for '+'Ria'+' cash payment on '+df['NRBCB Value/Paid Date'].dt.date.apply(str)
    tr_date = date.today()
    gl_df['br_code'] = df['BR Code']
    gl_df['date'] = tr_date
    gl_df['acc'] = exc.gl_no
    gl_df['cd'] = 'C'
    gl_df['amount'] = df['BDT']
    gl_df['narration'] = df['narration']
    gl_df['flag'] = 0
    return gl_df

def get_br_batch_transaction(df,batch_columns,name='RIA MONEY TRANSFER'):
    br_df = pd.DataFrame(columns=batch_columns)
    exc = ExchangeHouse.objects.get(name=name)
    df['narration'] = 'Ria'+' pmt fvg '+df['BR Code']+" on "+df['NRBCB Value/Paid Date'].dt.date.apply(str)
    br_df['narration'] = df['narration']
    tr_date = date.today()
    br_df['br_code'] = '0101'
    br_df['date'] = tr_date
    br_df['acc'] = exc.ac_no
    br_df['cd'] = 'D'
    br_df['amount'] = df['BDT']
    br_df['flag'] = 1
    return br_df
#Ria Pmt fvg 0135 on 14/02/2019(paid date)

def ria_batch(ex_df,branch_df):
    df = pd.merge(ex_df,branch_df)
    df = df.sort_values('User Name')
    gl_df= get_gl_batch_transaction(df,batch_columns)
    br_df= get_br_batch_transaction(df,batch_columns)
    df = pd.concat([gl_df,br_df])
    return df

def hellobello():
    p1 = Path("F:\\Projects\\Remittance Report\\May\\679. NRBCB Statement Payment date May 06, 2019.xls")
    p2 = Path("F:\\Projects\\Remittance Report\\march\\RIA BR MAP.xlsx")
    rdf = ria_excel_to_df(p1)
    bdf = pd.read_excel(p2,skiprows=[1,])
    bdf['BR Code'] = "0"+bdf['BR Code'].apply(str)
    df = ria_batch(rdf,bdf)
    return df
