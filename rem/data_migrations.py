from .models import *
from django.contrib.auth.models import User
import pandas as pd
from pathlib import Path


#df = pd.read_excel(('cdcng.xlsx'), dtype=object)

"""def change_sub_branch_code(booth, df):
    for i,r in df.iterrows():
        if booth.code == r['pn']:
            booth.code = r['new']
            booth.save()
            print(r['new'], booth.code, booth.name)"""

def get_all_cash_incentive_from_remittance_table(qset):
    for q in qset:
        try:
            c = CashIncentive()
            c.create_entry_from_remittance(q)
            #return True
        except Exception as e:
            print(e)


def get_all_country_from_reference(pathtoreference='REFERENCE_FILE.xlsm'):
    df = pd.read_excel(pathtoreference, 'COUNTRY', dtype=object)
    for inx, row in df.iterrows():
        try:
            cn = Country()
            cn.name = row['COUNTRY']
            cn.code = row['COUNTRY_ID']
            cn.save()
        except Exception as e:
            print(e)