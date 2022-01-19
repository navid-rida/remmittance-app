from schedules.models import Currency
import pandas as pd
from pathlib import Path


def get_all_currency_from_reference(pathtoreference='REFERENCE_FILE.xlsm'):
    df = pd.read_excel(Path(pathtoreference), 'CURRENCY', dtype=object)
    for inx, row in df.iterrows():
        try:
            cn = Currency()
            cn.name = row['UPPER(TRIM(CCY_LONG_NM))']
            cn.ccy_id = row['CCY_ID']
            cn.cur_code = row['CUR_CODE']
            cn.short = row['CURRENCY']
            cn.save()
        except Exception as e:
            print(e)
    print('Done')



for ix, row in df2.iterrows():
    for item in q:
        if item.ccy_id==row['CCY_ID'] and item.short != row['CURRENCY']:
            item.short = row['CURRENCY']
            item.save()


for item in q:
    if item.cur_code == 'nan':
        item.cur_code = None
        item.save()