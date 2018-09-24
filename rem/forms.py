from .models import Remmit, ExchangeHouse, Branch
from django.forms import ModelForm
from django import forms
#from datetime import date
from django.utils import timezone
from .validators import *

class RemmitForm(ModelForm):

    class Meta:
        model = Remmit
        fields = ('exchange','rem_country','reference','sender','reciever','amount','date',)
        widgets = {
            'date': forms.SelectDateWidget,
        }


    def clean(self):
        cleaned_data = super().clean()
        exchange = cleaned_data.get("exchange")
        reference = cleaned_data.get("reference")
        if exchange.name == 'WESTERN UNION':
            validate_western_code(reference)
        elif exchange.name == 'XPRESS MONEY':
            validate_xpress(reference)
        elif exchange.name == 'RIA MONEY TRANSFER':
            validate_ria(reference)
        elif exchange.name == 'PLACID EXPRESS':
            validate_placid(reference)
        elif exchange.name == 'MONEYGRAM':
            validate_moneygram(reference)
        else:
            raise forms.ValidationError(
                    "The reference number does not match with any known third party remittance services "
                )



class CsvForm(forms.Form):
    date = forms.DateField(label="Date for download", initial=timezone.now, widget=forms.SelectDateWidget)

class SearchForm(forms.Form):
    #date_from = forms.DateField(label="Starting Date", initial=timezone.now, required=False, input_formats=['%d/%m/%Y','%d/%m/%y','%d-%m-%Y','%d-%m-%y','%Y-%m-%d','%Y/%m/%d'])
    #date_to = forms.DateField(label="Ending Date", initial=timezone.now, required=False, input_formats=['%d/%m/%Y','%d/%m/%y','%d-%m-%Y','%d-%m-%y','%Y-%m-%d','%Y/%m/%d'])
    date_from = forms.DateField(label="Starting Date", initial=timezone.now, required=False, widget=forms.SelectDateWidget)
    date_to = forms.DateField(label="Ending Date", initial=timezone.now, required=False, widget=forms.SelectDateWidget)
    exchange = forms.ModelChoiceField(queryset=ExchangeHouse.objects.all(),required=False)
    branch = forms.ModelChoiceField(queryset=Branch.objects.all().order_by('name'),required=False)
