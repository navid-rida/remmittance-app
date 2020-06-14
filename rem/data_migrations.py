from .models import *
from django.contrib.auth.models import User
import pandas as pdb
from pathlib import Path


df = pd.read_excel('cdcng.xlsx'), dtype=object)

def change_sub_branch_code(booth, df):
    for i,r in df.iterrows():
        if booth.code == r['pn']:
            booth.code = r['new']
            booth.save()
            print(r['new'], booth.code, booth.name)
