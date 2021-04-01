import pandas as pd
from rem.remreport import get_file_list
import calendar

from .models import *


p = 'F:\\Projects\\Remittance Report\\BB Month year\\BB Report'
#p2 = 'F:\\Projects\\Remittance Report\\FCR 1 2 3 July 18_PB.xlsx'

sorted_columns = ['year', 'month','country','count20000', 'sum20000','count50000','sum50000','count100000','sum100000','count150000','sum150000','count99999999999', 'sum99999999999','total_count','total_sum']
xllist= get_file_list(p,ext='.xlsx')
col = ['date','bank','sl','BRANCH','REPORT TYPE','SCHEDULE CODE','TYPE CODE','PURPOSE CODE','CURRENCY','COUNTRY','DISTRICT','NID','PASSPORT','amount']

def get_merged_xl(xllist,col):
    df = pd.DataFrame()
    for file in xllist:
        df_single_file=pd.DataFrame()
        df_single_file = pd.read_excel(file,header=None, names=col,skiprows=[0,1])
        df = df.append(df_single_file)
    return df

df = get_merged_xl(xllist,col)

#df2 = pd.read_excel(p2, sheet_name='Raw', names=col, header=None, skiprows=[0,1])

c = ['SAUDI ARABIA','UNITED ARAB EMIRATES (UAE)','UNITED STATES OF AMERICA (USA)','KUWAIT','MALAYSIA','UNITED KINGDOM (UK)','QATAR','OMAN']


#df3 = df.append(df2)

slabs= [0,20000,50000,100000,150000,99999999999]

def get_sum_count(df, year, month, country,slab, c=['SAUDI ARABIA','UNITED ARAB EMIRATES (UAE)','UNITED STATES OF AMERICA (USA)','KUWAIT','MALAYSIA','UNITED KINGDOM (UK)','QATAR','OMAN']):
    #left =
    df = df[(df['date'].dt.year==year) & (df['date'].dt.month==month) & (slabs[slab-1]<df['amount']) & (df['amount']<=slabs[slab])]
    if country in c:
        df= df[df['COUNTRY']==country]
    else:
        df= df[~df['COUNTRY'].isin(c)]
    sum = df['amount'].sum()
    count = df['amount'].count()
    return sum,count

def get_row(df, year, month,country, slabs= [0,20000,50000,100000,150000,99999999999]):
    dc = {}
    total_sum=0
    total_count=0
    for slab in slabs:
        if slab!=0:
            sum, count = get_sum_count(df,year, month,country,slabs.index(slab))
            dc['year']= year
            dc['month']= calendar.month_name[month]
            dc['country']= country
            dc['count'+str(slab)]= count
            dc['sum'+str(slab)]= sum
            total_count=total_count+count
            total_sum=total_sum+sum
    dc['total_sum'] = total_sum
    dc['total_count'] = total_count
    return dc

def get_worksheet(df, years=[2018,2019]):
    new_df = pd.DataFrame()
    for year in years:
        for month in range(7,13):
            for country in ['SAUDI ARABIA','UNITED ARAB EMIRATES (UAE)','UNITED STATES OF AMERICA (USA)','KUWAIT','MALAYSIA','UNITED KINGDOM (UK)','QATAR','OMAN','Global']:
                row = get_row(df, year, month,country)
                series = pd.Series(row)
                new_df = new_df.append(series, ignore_index=True)
    #new_df new_df.sort_values(by=['year', 'month','country','count20000', 'sum20000','count50000','sum50000','count100000','sum100000','count150000','sum150000','count99999999999', 'sum99999999999',])
    return new_df


