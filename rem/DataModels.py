from .models import *
import pandas as pd
from datetime import datetime, date
import io

####################### common functions#################################################

def excel_output(df):
    output = io.BytesIO()
    #time = str(date.today())
    #filename = "output "+time+".xlsx"
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    #writer.book.filename = io
    df.to_excel(writer,'Sheet1', index=False, header=False)
    writer.save()
    xlsx_data = output.getvalue()
    return xlsx_data

####################### common functions#################################################
def make_ac_df(list,category,columns):
    #day = date.strftime('%Y-%m-%d')
    dict = {}
    remmits = Remmit.objects.filter(id__in=list)
    #Sl= []
    tr_date = []
    br_code = []
    ac_no = []
    type = []
    amount = []
    narrations = []
    flags = []
    i = 1
    for rem in remmits:
        #Sl.append(i)
        #i = i + 1
        dr_cr = 'C' if category=='gl' else 'D'
        tr_date.append(date.today().strftime('%d/%m/%Y'))
        #br_code.append(rem.branch.code)
        if category=='gl':
            br_code.append(rem.branch.code)
        else:
            br_code.append("0101")
        if category=='gl':
            ac_no.append(rem.exchange.gl_no)
        else:
            ac_no.append(rem.exchange.ac_no)
        type.append(dr_cr)
        amount.append(rem.amount)
        if dr_cr == 'C':
            narration = "Settlement agt "+ rem.reference +" made on "+rem.date.strftime('%d/%m/%Y')
        else:
            narration = "Favoring "+rem.branch.name+" agt "+ rem.reference +" made on "+rem.date.strftime('%d/%m/%Y')
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
        'ac_no' : ac_no,
        'type' : type,
        'amount' : amount,
        'narrations' : narrations,
        'flags' : flags
        }
    df = pd.DataFrame(dict)
    df = df.sort_values(by=['ac_no',])
    return df

def rem_bb_summary(list):
    columns=['date', 'br_code', 'ac_no', 'type', 'amount', 'narration', 'flag']
    gl_df = make_ac_df(list,'gl',columns)
    ac_df = make_ac_df(list,'br_ac',columns)
    frames = [gl_df, ac_df]
    complete_df = pd.concat(frames)
    return complete_df
