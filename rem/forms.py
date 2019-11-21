from .models import Remmit, ExchangeHouse, Branch, Receiver, Requestpay, Country,Booth
from django.forms import ModelForm
from django import forms
from datetime import date, timedelta
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
    date_sending = forms.DateField(widget=forms.TextInput(attrs={'placeholder': 'dd/mm/yy'}), input_formats=['%d/%m/%Y','%d-%m-%Y','%Y-%m-%d'])

    class Meta:
        model = Remmit
        fields = ('exchange','rem_country','reference','sender','amount','relationship', 'purpose','date_sending','unpaid_cash_incentive_reason', 'cash_incentive_status','sender_occupation','currency')
        widgets = {
            #'dob': forms.SelectDateWidget,
            #'cash_incentive_status': forms.RadioSelect,
            #'dob': forms.DateInput(format = ['%d/%m/%Y','%d-%m-%Y','%Y-%m-%d']),
            #'idissue': forms.DateInput(format = ['%d/%m/%Y','%d-%m-%Y','%Y-%m-%d']),
            #'idexpire': forms.DateInput(format['%d/%m/%Y','%d-%m-%Y','%Y-%m-%d']),
        }

    def __init__(self, *args, **kwargs):
            super(RemmitForm, self).__init__(*args, **kwargs)
            self.fields['rem_country'].queryset = Country.objects.exclude(name="BANGLADESH")

    def clean_unpaid_cash_incentive_reason(self):
        unpaid_cash_incentive_reason = self.cleaned_data['unpaid_cash_incentive_reason']
        cash_incentive_status = self.cleaned_data['cash_incentive_status'] if 'cash_incentive_status' in self.cleaned_data else None
        if cash_incentive_status == 'U' and unpaid_cash_incentive_reason==None:
            raise ValidationError('Reason is required if cash incentive status is unpaid')
        # Always return a value to use as the new cleaned data, even if
        # this method didn't change it.
        return unpaid_cash_incentive_reason

    def clean_cash_incentive_status(self):
        cash_incentive_status = self.cleaned_data['cash_incentive_status']
        if 'cash_incentive_status' in self.changed_data and cash_incentive_status=='U' and self.fields['cash_incentive_status'].initial=="":
            raise ValidationError('Validation error: A remittance cannot be marked unpaid once it is paid')
        # Always return a value to use as the new cleaned data, even if
        # this method didn't change it.
        return cash_incentive_status

    def clean_date_sending(self):
        date_sending = self.cleaned_data['date_sending']
        if date_sending < timezone.now().date() - timedelta(days=90):
            raise ValidationError('Validation error: date is too far away')
        if date_sending > timezone.now().date():
            raise ValidationError('Date Sending cannot be a future date')
        # Always return a value to use as the new cleaned data, even if
        # this method didn't change it.
        return date_sending

    def clean(self):
        cleaned_data = super().clean()
        exchange = cleaned_data.get("exchange")
        reference = cleaned_data.get("reference")
        cash_incentive_status = cleaned_data.get("cash_incentive_status")
        unpaid_cash_incentive_reason = cleaned_data.get("unpaid_cash_incentive_reason")
        #if 'cash_incentive_status' in form.changed_data:
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
        fields = ('name','cell','address','dob','idtype','idno','idissue','idexpire','ac_no')
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

class MultipleSearchForm(forms.Form):
    #cell = forms.CharField(label="Enter Customer's Cell No.", validators=[validate_mobile])
    keyword = forms.CharField(label="Enter reference number, name or phone no")

class SettlementForm(forms.Form):
    SETTLE_CHOICES= (('remittance','Remittance Settlement'),('cash_incentive','Cash Incentive Settlement'))
    settlemnt_type = forms.ChoiceField(label="Settlement Type",choices=SETTLE_CHOICES, required=True)
    batchfile = forms.FileField(label="Upload Batch File", required=True)

class SearchForm(forms.Form):
    #date_from = forms.DateField(label="Starting Date", initial=timezone.now, required=False, input_formats=['%d/%m/%Y','%d/%m/%y','%d-%m-%Y','%d-%m-%y','%Y-%m-%d','%Y/%m/%d'])
    #date_to = forms.DateField(label="Ending Date", initial=timezone.now, required=False, input_formats=['%d/%m/%Y','%d/%m/%y','%d-%m-%Y','%d-%m-%y','%Y-%m-%d','%Y/%m/%d'])
    #date_from = forms.DateField(label="Starting Date", initial=timezone.now, required=False, widget=forms.SelectDateWidget)
    date_from = forms.DateField(label="Starting Date", initial= timezone.now, required=False, input_formats=['%d/%m/%Y','%d-%m-%Y','%Y-%m-%d'], localize=True)
    date_to = forms.DateField(label="Ending Date", initial= timezone.now,  required=False, input_formats=['%d/%m/%Y','%d-%m-%Y','%Y-%m-%d'], localize=True)
    exchange = forms.ModelChoiceField(queryset=ExchangeHouse.objects.all(),required=False)
    branch = forms.ModelChoiceField(queryset=Branch.objects.all().order_by('name'),required=False)
    booth = forms.ModelChoiceField(queryset=Booth.objects.all().order_by('name'),required=False)
    BRANCH_BOOTH_CHOICES= (('all','All'),('branch','Only Branch'),('booth','Only Booth'))
    BranchBooth = forms.ChoiceField(label="Branch/ Booth",choices=BRANCH_BOOTH_CHOICES, required=False)
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
    keyword = forms.CharField(label="Reference/Benificiary Cell", required=False)

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

class SignUpForm(RegistrationForm):
    branch = forms.ModelChoiceField(queryset=Branch.objects.all().order_by('name'),validators=[validate_user_limit])
    booth = forms.ModelChoiceField(queryset=Booth.objects.all().order_by('name'),validators=[validate_booth_user_limit],required=False)
    cell = forms.CharField(label="Mobile No.", validators=[validate_mobile])
    email = forms.EmailField(max_length=254, help_text='Input your official Email address',validators=[validate_nrbc_mail])

    class Meta:
        model = User
        fields=('username', 'first_name', 'last_name','branch','booth', 'cell', 'email', 'password1', 'password2',)

    def clean_booth(self):
        booth = self.cleaned_data['booth']
        if booth:
            branch = self.cleaned_data['branch']
        #idtype = self.cleaned_data['idtype']
            if branch != booth.branch:
                raise ValidationError('BRANCH-BOOTH MISMATCH')
        # Always return a value to use as the new cleaned data, even if
        # this method didn't change it.
        return booth

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
