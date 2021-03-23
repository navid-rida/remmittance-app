import xml.etree.ElementTree as ET
import os
import pandas as pd
import numpy as np
from pathlib import Path

def check_xml(file):
    file_ext = dir.suffixes[len(dir.suffixes)-1]
    if file_ext == '.xml':
        return True

def get_xml_list(file_list):
    #file_list = os.listdir(path)
    xmllist = []
    for file in file_list:
        root = ET.parse(file).getroot()
        xmllist.append(root)
    return xmllist

def get_file_list(path='.',ext='.xml'):
    p = Path(path)
    files = []
    for dir in p.iterdir():
        if not dir.is_dir():
            file_ext = dir.suffixes[len(dir.suffixes)-1]
            if file_ext == ext:
                files.append(dir.resolve())
    return files

def merge_xml(xmllist):
    first_xml = xmllist[0]
    for xml_file in xmllist[1:]:
        first_xml.extend(xml_file)
    return first_xml


def xml_to_df(xmlfile):
    transaction_list = xmlfile.findall('transaction')
    branch_list = []
    code_list = []
    amount_list = []
    internal_ref_list = []
    ac_list = []
    for tr in transaction_list:
        for branch in tr.iter('branch'):
            branch_name = branch.text
            #name, code = branch_tag.split("-")
            branch_list.append(branch_name)
            #code_list.append(code)
            #break
        for acc in tr.iter('account'):
            ac_no = acc.text
            #name, code = branch_tag.split("-")
            ac_list.append(ac_no)
            #code_list.append(code)
            #break
        amount_list.append(tr.find('amount_local').text)
        internal_ref_list.append(tr.find('internal_ref_number').text)
    dict = {#'Branch Code':code_list,
            'Internal_Ref': internal_ref_list,
            'Branch': branch_list,
            'Account': ac_list,
            'Amount': amount_list,
            }
    df = pd.DataFrame(dict)
    return df


def get_file_number_from_file_name(file_path):
    """ Input and XML file path and returns file number
    (CTR XML serial generated from systmem)"""
    file_number = file_path.stem.split('--')[0].split('-')[-1]
    return file_number

def rename_file(file_path_old, file_number, year, month):
    """ Rename XML file for upload.
    Use the file_number as serial for new file name
    and includes month and date"""
    new_name = "NRBCB-CTR-"+month+"-"+year+"-"+str(file_number)+".xml"
    target_path = file_path_old.with_name(new_name)
    try:
        file_path_old.rename(target_path)
        return True
    except:
        return False

def rename_all_files_in_path(folder_path, year, month):
    lst = get_file_list(folder_path)
    for file in lst:
        number = get_file_number_from_file_name(file)
        rename = rename_file(file, number, year, month)
        if not rename:
            print("File number Cannot be renamed")
    print("Done")




"""def xml_to_df(xmlfile):
    transaction_list = xmlfile.findall('transaction')
    for tr in transaction_list:
        return df"""

def lola(path='.'):
    path = Path(path)
    file_list = get_file_list(path)
    xml_list = get_xml_list(file_list)
    merged_xml = merge_xml(xml_list)
    df = xml_to_df(merged_xml)
    df['Amount'] = df['Amount'].apply(float)
    df = df[['Branch','Amount']].groupby('Branch').agg([np.sum,np.size])
    return df

"""____________________________________________________________________________________________________________________________________________"""

def get_tree_list(file_list):
    tree_list = []
    for file in file_list:
        tree = ET.parse(file)
        tree_list.append(tree)
    return tree_list

def modify_transaction_location(tree,location_dict):
    root = tree.getroot()
    for element in root.iter('transaction_location'):
        if element.text in location_dict.keys():
            element.text = location_dict[element.text]
    return tree

def modify_transaction_branch(tree,branch_dict):
    root = tree.getroot()
    for element in root.iter('branch'):
        if element.text in branch_dict.keys():
            element.text = branch_dict[element.text]
    return tree

def build_file_name(month,year,i):
    name = 'NRBCB-'+month+"-"+year+"-"+str(i)+".xml"
    return name


def vola(folder_path='F:\\Reporting\\CTR\\2019\\april\\temp',xl_path='F:\\Reporting\\CTR\\2019\\april\\ctr_location.xlsx', month='APR', year='2019'):
    f_p = Path(folder_path)
    xl_p = Path(xl_path)
    file_list = get_file_list(f_p)
    tree_list = get_tree_list(file_list)
    xl = pd.read_excel(xl_p)
    lc_list = list(xl['location'])
    loc_dis_list = list(xl['loc_dis'])
    loc_dis_dict = dict(zip(lc_list,loc_dis_list))
    br_list = list(xl['Branch'])
    br_dis_list = list(xl['br_dist'])
    br_dis_dict = dict(zip(br_list,br_dis_list))
    i=2
    for tree in tree_list:
        tree = modify_transaction_location(tree, loc_dis_dict)
        tree = modify_transaction_branch(tree, br_dis_dict)
        file_name = build_file_name(month,year,i)
        path = Path(f_p,'processed',file_name)
        tree.write(path)
        i=i+1
    #df = xml_to_df(merged_xml)
    return 0
