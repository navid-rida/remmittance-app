import pandas as pd
import xml.etree.ElementTree as ET


def check_combined_phone(phone_no):
    """ Checks if a phone value is comma seperated and more than one.
        return True if double or more"""
    if ',' in phone_no and len(phone_no.split(','))>1:
        return True

def make_phone_node(phone_no, com_type, con_type):
    """Makes phone Node, returns Element object """
    phone = ET.Element("phone")
    phone.append("tph_contact_type") # Contact type
    phone.append("tph_communication_type") # Communication type
    phone.append("tph_number") # Phone Number
    


class XMLFile():

    def __init__(self, file_path):
        self.root = ET.parse(file_path).getroot()
        self.file_name = file_path.name
        self.transaction_list = self.root.findall('transaction')

    def get_combined_phone_nodes(self):
        """ Gets all phone nodes with more than one phone
            seperated by comma. returns list of nodes"""
        phone_list = []
        for transaction in self.transaction_list:
            for phone in transaction.findall('.//phone'):
                if check_combined_phone(phone.find('tph_number').text):
                    phone_list.append(phone)
        return phone_list

    def set_seperate_phone_nodes(self):
        """ checks for phone nodes with double or more phone no,
            if found, adds phone nodes with single phone no and on_delete
            the node with more than one phone"""
        phones_list = []
        for phones_node in self.root.findall('.//phones'):
            for phone in phones_node:
                if check_combined_phone(phone.find('tph_number').text):
                    ph_list = phone.find('tph_number').text.split(',')
