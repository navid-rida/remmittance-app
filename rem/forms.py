from .models import Remmit, ExchangeHouse, Branch, Receiver, Requestpay
from django.forms import ModelForm
from django import forms
#from datetime import date
from django.utils import timezone
from .validators import *

class RemmitForm(ModelForm):

    class Meta:
        model = Remmit
        fields = ('exchange','rem_country','reference','sender','amount',)
        """widgets = {
            'date': forms.SelectDateWidget,
        }"""


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


class ReceiverForm(ModelForm):

    class Meta:
        model = Receiver
        fields = ('name','cell','address','dob','idtype','idno','idissue','idexpire')
        widgets = {
            'dob': forms.SelectDateWidget,
        }
    def clean_idno(self):
        idno = self.cleaned_data['idno']
        idtype = self.cleaned_data['idtype']
        if idtype == 'NID':
            if len(idno)<13:
                validate_smart_nid(idno)
            else:
                validate_old_nid(idno)
        elif idtype=='PASSPORT':
            validate_passport(idno)
        else:
            validate_bc(idno)
        # Always return a value to use as the new cleaned data, even if
        # this method didn't change it.
        return idno


class ReceiverSearchForm(forms.Form):
    #cell = forms.CharField(label="Enter Customer's Cell No.", validators=[validate_mobile])
    identification = forms.CharField(label="Enter NID/Passport/ Birth Certificate No.")

class SearchForm(forms.Form):
    #date_from = forms.DateField(label="Starting Date", initial=timezone.now, required=False, input_formats=['%d/%m/%Y','%d/%m/%y','%d-%m-%Y','%d-%m-%y','%Y-%m-%d','%Y/%m/%d'])
    #date_to = forms.DateField(label="Ending Date", initial=timezone.now, required=False, input_formats=['%d/%m/%Y','%d/%m/%y','%d-%m-%Y','%d-%m-%y','%Y-%m-%d','%Y/%m/%d'])
    #date_from = forms.DateField(label="Starting Date", initial=timezone.now, required=False, widget=forms.SelectDateWidget)
    date_from = forms.DateField(label="Starting Date", initial=timezone.now, required=False, input_formats=['%d/%m/%Y','%d-%m-%Y','%Y-%m-%d'])
    date_to = forms.DateField(label="Ending Date", initial=timezone.now, required=False, input_formats=['%d/%m/%Y','%d-%m-%Y','%Y-%m-%d'])
    exchange = forms.ModelChoiceField(queryset=ExchangeHouse.objects.all(),required=False)
    branch = forms.ModelChoiceField(queryset=Branch.objects.all().order_by('name'),required=False)
    REVIEW= 'RV'
    REJECTED = 'RJ'
    PAID = 'PD'
    STATUS_CHOICES = (
        (REVIEW,'Request staged for review'),
        (REJECTED, 'Request rejected'),
        (PAID, 'Amount paid to customer'),
        )
    status = forms.ChoiceField(choices=STATUS_CHOICES,required=False)

class PaymentForm(forms.Form):
    comment = forms.CharField(label="Remarks", widget=forms.Textarea, required=False)
    PAID = 'P'
    REJECTED = 'R'
    PAYMENT_CHOICES = (
        (PAID,'Confirm Payment'),
        (REJECTED, 'Reject Request'),
        )
    confirmation = forms.ChoiceField(choices=PAYMENT_CHOICES, widget=forms.RadioSelect, required=True)
    req = forms.ModelChoiceField(queryset=Requestpay.objects.filter(status='RV'),required=False)
    screenshot = forms.ImageField(required=False)


    def clean(self):
        cleaned_data = super().clean()
        confirmation = cleaned_data.get("confirmation")
        comment = cleaned_data.get("comment")
        screenshot = cleaned_data.get('screenshot', False)
        if (confirmation=='R') and (not comment):
            raise forms.ValidationError(
                    "A remark must be entered if the payment is rejected"
                )
        elif (confirmation=='P') and (not screenshot):
            raise forms.ValidationError(
                    "Payment confirmationa screenshot not uploaded"
                )
        """else:
            raise forms.ValidationError(
                    "Please confirm or reject the payment"
                )"""
