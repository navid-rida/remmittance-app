import pandas as pd
import xml.etree.ElementTree as ET
from rem.remreport import hellopops

fp= 'F:\\Projects\\Exporter XML\\20190929\\'


def exporter_xml(path,ext='.xls'):
    df = hellopops(path=path,ext=ext)
    i = 1
    xplist = ET.Element('EXPORTER_LIST')
    for index, series in df.iterrows():
        exp = ET.SubElement(xplist,'EXPORTER')
        sl = ET.SubElement(exp,'SL_NO')
        sl.text=str(i)
        i=i+1
        erc = ET.SubElement(exp,'ERC_NO')
        erc.text=str(series['ERC NO.'])
        name = ET.SubElement(exp,'EXPORTER_NAME')
        name.text=series['EXPORTER NAME']
        phone = ET.SubElement(exp,'CONTACT_NO')
        phone.text=str(series['CONTACT NO.'])
        email = ET.SubElement(exp,'EMAIL')
        email.text=series['E-MAIL']
        area = ET.SubElement(exp,'EXPORTER_AREA')
        area.text="01"
    tree = ET.ElementTree(xplist)
    return tree

groot = exporter_xml(fp)
#tree.write("ho-cpu.xml")
