from .models import Remmit, ExchangeHouse, Branch, Receiver, Requestpay, Country
from django.forms import ModelForm
from django import forms
#from datetime import date,datetime
from django.utils import timezone
from .validators import *
#import floppyforms as floppy
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.conf import settings
from django.db import transaction
############### imports for django-registration #############################
from django_registration.forms import RegistrationForm, RegistrationFormUniqueEmail


class RemmitForm(ModelForm):

    class Meta:
        model = Remmit
        fields = ('exchange','rem_country','reference','sender','amount','relationship', 'purpose')

    def __init__(self, *args, **kwargs):
            super(RemmitForm, self).__init__(*args, **kwargs)
            self.fields['rem_country'].queryset = Country.objects.exclude(name="BANGLADESH")


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


class RemittInfoForm(RemmitForm):
    screenshot = forms.ImageField(required=True)

class ReceiverForm(ModelForm):
    dob = forms.DateField(widget=forms.TextInput(attrs={'placeholder': 'dd/mm/yy'}), label="Date of Birth",input_formats=['%d/%m/%Y','%d-%m-%Y','%Y-%m-%d'])
    idissue = forms.DateField(widget=forms.TextInput(attrs={'placeholder': 'dd/mm/yy'}), label="ID Issue Date",input_formats=['%d/%m/%Y','%d-%m-%Y','%Y-%m-%d'], required=False)
    idexpire = forms.DateField(widget=forms.TextInput(attrs={'placeholder': 'dd/mm/yy'}),label="ID Expiry date",input_formats=['%d/%m/%Y','%d-%m-%Y','%Y-%m-%d'], required=False)

    class Meta:
        model = Receiver
        fields = ('name','cell','address','dob','idtype','idno','idissue','idexpire')
        widgets = {
            #'dob': forms.SelectDateWidget,
            'address': forms.Textarea(attrs={'rows':4, 'cols':45}),
            #'dob': forms.DateInput(format = ['%d/%m/%Y','%d-%m-%Y','%Y-%m-%d']),
            #'idissue': forms.DateInput(format = ['%d/%m/%Y','%d-%m-%Y','%Y-%m-%d']),
            #'idexpire': forms.DateInput(format['%d/%m/%Y','%d-%m-%Y','%Y-%m-%d']),
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

    def clean_idissue(self):
        idissue = self.cleaned_data['idissue']
        #idtype = self.cleaned_data['idtype']
        if idissue and idissue > timezone.now().date():
            raise ValidationError('ID Issue date cannot be a future date')
        # Always return a value to use as the new cleaned data, even if
        # this method didn't change it.
        return idissue


class ReceiverSearchForm(forms.Form):
    #cell = forms.CharField(label="Enter Customer's Cell No.", validators=[validate_mobile])
    identification = forms.CharField(label="Enter NID/Passport/ Birth Certificate No.")

class SearchForm(forms.Form):
    #date_from = forms.DateField(label="Starting Date", initial=timezone.now, required=False, input_formats=['%d/%m/%Y','%d/%m/%y','%d-%m-%Y','%d-%m-%y','%Y-%m-%d','%Y/%m/%d'])
    #date_to = forms.DateField(label="Ending Date", initial=timezone.now, required=False, input_formats=['%d/%m/%Y','%d/%m/%y','%d-%m-%Y','%d-%m-%y','%Y-%m-%d','%Y/%m/%d'])
    #date_from = forms.DateField(label="Starting Date", initial=timezone.now, required=False, widget=forms.SelectDateWidget)
    date_from = forms.DateField(label="Starting Date", initial= timezone.now, required=False, input_formats=['%d/%m/%Y','%d-%m-%Y','%Y-%m-%d'], localize=True)
    date_to = forms.DateField(label="Ending Date", initial= timezone.now,  required=False, input_formats=['%d/%m/%Y','%d-%m-%Y','%Y-%m-%d'], localize=True)
    exchange = forms.ModelChoiceField(queryset=ExchangeHouse.objects.all(),required=False)
    branch = forms.ModelChoiceField(queryset=Branch.objects.all().order_by('name'),required=False)
    REVIEW= 'RV'
    REJECTED = 'RJ'
    PAID = 'PD'
    ALL = 'AL'
    STATUS_CHOICES = (
        (ALL,'All Request'),
        (REVIEW,'Pending For Processing'),
        (REJECTED, 'Rejected'),
        (PAID, 'Paid'),
        )
    status = forms.ChoiceField(label='Request Status',choices=STATUS_CHOICES,required=False)

class PaymentForm(forms.Form):
    comment = forms.CharField(label="Remarks", widget=forms.Textarea(attrs={'rows':4, 'cols':45}), required=False)
    PAID = 'P'
    REJECTED = 'R'
    PAYMENT_CHOICES = (
        (PAID,'Confirm Payment'),
        (REJECTED, 'Reject Request'),
        )
    confirmation = forms.ChoiceField(choices=PAYMENT_CHOICES, widget=forms.RadioSelect, required=True)
    req = forms.ModelChoiceField(queryset=Requestpay.objects.filter(status='RV'),required=False)
    screenshot = forms.ImageField(required=False)
    agent_screenshot = forms.ImageField(required=False)
    customer_screenshot = forms.ImageField(required=False)
    western_trm_screenshot = forms.ImageField(required=False)


    def clean(self):
        cleaned_data = super().clean()
        confirmation = cleaned_data.get("confirmation")
        comment = cleaned_data.get("comment")
        agent_screenshot = cleaned_data.get('agent_screenshot', False)
        customer_screenshot = cleaned_data.get('customer_screenshot', False)
        western_trm_screenshot = cleaned_data.get('western_trm_screenshot', False)
        if (confirmation=='R') and (not comment):
            raise forms.ValidationError(
                    "A remark must be entered if the payment is rejected"
                )
        elif (confirmation=='P') and (not agent_screenshot):
            raise forms.ValidationError(
                    "Agent copy screenshot not uploaded"
                )
        """else:
            raise forms.ValidationError(
                    "Please confirm or reject the payment"
                )"""

class SignUpForm(RegistrationFormUniqueEmail):
    #first_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    #last_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    #email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')
    branch = forms.ModelChoiceField(queryset=Branch.objects.all().order_by('name'),validators=[validate_user_limit])
    cell = forms.CharField(label="Mobile No.", validators=[validate_mobile])
    email = forms.EmailField(max_length=254, help_text='Input your official Email address',validators=[validate_nrbc_mail])

    class Meta:
        model = User
        fields=('username', 'first_name', 'last_name','branch', 'cell', 'email', 'password1', 'password2',)

    """def clean(self):
        cleaned_data = super().clean()
        branch = cleaned_data.get("branch")
        user_number = branch.employee_set.filter(user__is_active=True).count()
        MAXIMUM_AllOWWED_USER_PER_BRANCH = settings.MAXIMUM_USER_PER_BRANCH
        if user_number >= MAXIMUM_AllOWWED_USER_PER_BRANCH:
            raise forms.ValidationError(
                    "maximum user limit for the branch exceeded"
                )
        else:
            cleaned_data["branch"] = branch

        return cleaned_data"""
