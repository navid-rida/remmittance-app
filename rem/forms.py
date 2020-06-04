from .models import Remmit, ExchangeHouse, Branch, Receiver, Requestpay, Country,Booth, Claim
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
################## Crispy forms ########################
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit #, Fieldset, ButtonHolder, Submit


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

    def clean_currency(self):
        currency = self.cleaned_data['currency']
        exchange = self.cleaned_data['exchange']
        exchange_list = ['WESTERN UNION','XPRESS MONEY','RIA MONEY TRANSFER','PLACID EXPRESS','MONEYGRAM']
        if (exchange.name in exchange_list) and (currency.name!='BANGLADESHI TAKA'):
            raise ValidationError('Only BDT can be selected for '+exchange.name )
        # Always return a value to use as the new cleaned data, even if
        # this method didn't change it.
        return currency


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
        exclude = ['created_by']
        widgets = {
            #'dob': forms.SelectDateWidget,
            'address': forms.Textarea(attrs={'rows':4, 'cols':45}),
            #'dob': forms.DateInput(format = ['%d/%m/%Y','%d-%m-%Y','%Y-%m-%d']),
            #'idissue': forms.DateInput(format = ['%d/%m/%Y','%d-%m-%Y','%Y-%m-%d']),
            #'idexpire': forms.DateInput(format['%d/%m/%Y','%d-%m-%Y','%Y-%m-%d']),
        }

    def __init__(self, *args, **kwargs):
        super(ReceiverForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'name',
            'gender',
            'father_name',
            'mother_name',
            'spouse_name',
            'profession',
            'nationality',
            'ac_no',
            'address',
            Field('dob', css_class="date"),
            'cell',
            'idtype',
            Field('idissue', css_class="date"),
            Field('idexpire', css_class="date"),
            'idno',
            Submit('submit', 'CREATE')
        )

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
        elif idtype=='DL':
            validate_alpha_num(idno)
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

    def clean_father_name(self):
        father = self.cleaned_data["father_name"]
        gender = self.cleaned_data["gender"]
        if gender=='M' and father==None:
            raise ValidationError('Father name is required')
        # Always return a value to use as the new cleaned data, even if
        # this method didn't change it.
        return father


    def clean_nationality(self):
        country = self.cleaned_data["nationality"]
        bd = Country.objects.get(name='BANGLADESH')
        if country!=bd:
            raise ValidationError('Only bangladeshi citizens are allowed')
        # Always return a value to use as the new cleaned data, even if
        # this method didn't change it.
        return country


    def clean(self):
        cleaned_data = super().clean()
        father = cleaned_data.get("father_name")
        spouse = cleaned_data.get("spouse_name")
        gender = cleaned_data.get("gender")
        #unpaid_cash_incentive_reason = cleaned_data.get("unpaid_cash_incentive_reason")
        #if 'cash_incentive_status' in form.changed_data:
        if gender=='F' and (father==None and spouse==None):
             raise forms.ValidationError(
                    "Either father name or husbands name is required"
                )

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
    booth = forms.ModelChoiceField(label='Sub-branch',queryset=Booth.objects.all().order_by('name'),required=False)
    BRANCH_BOOTH_CHOICES= (('all','All'),('branch','Only Branch'),('booth','Only Sub-branch'))
    BranchBooth = forms.ChoiceField(label="Branch/ Sub-branch",choices=BRANCH_BOOTH_CHOICES, required=False)
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

class SignUpForm(RegistrationFormUniqueEmail):
    branch = forms.ModelChoiceField(queryset=Branch.objects.all().order_by('name'),validators=[validate_user_limit])
    booth = forms.ModelChoiceField(label='Sub-branch',queryset=Booth.objects.all().order_by('name'),validators=[validate_booth_user_limit],required=False)
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
                raise ValidationError('BRANCH-SUB_BRANCH MISMATCH')
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

NO_VISA_CHOICES = (
            (None, "Not Applicable"),
            (True, "Obtained"),
            (False, "Not Obtained"),
           )

CHOICES = (
            (False, "NO"),
            (True, "YES")
           )

class ClaimForm(ModelForm):
    date_account_credit = forms.DateField(widget=forms.TextInput(attrs={'placeholder': 'dd/mm/yy'}), label="Date of Account Credit", input_formats=['%d/%m/%Y','%d-%m-%Y','%Y-%m-%d'])
    doc_expire = forms.DateField(widget=forms.TextInput(attrs={'placeholder': 'dd/mm/yy'}),label="Expiry Date of Remitter's Other Document", input_formats=['%d/%m/%Y','%d-%m-%Y','%Y-%m-%d'])
    passport_expire = forms.DateField(widget=forms.TextInput(attrs={'placeholder': 'dd/mm/yy'}), label= "Expiry Date of Remitter's Passport", input_formats=['%d/%m/%Y','%d-%m-%Y','%Y-%m-%d'])

    class Meta:
        model = Claim
        #fields = ('name','cell','address','dob','idtype','idno','idissue','idexpire','ac_no')
        exclude =('branch','created_by','date_forward','date_resolved')
        widgets = {
            #'dob': forms.SelectDateWidget,
            'visa_check': forms.Select(choices = NO_VISA_CHOICES),
            'statement_check': forms.Select(choices = CHOICES),
            'document_check': forms.Select(choices = CHOICES),
            'letter_check': forms.Select(choices = CHOICES),
            #'address': forms.Textarea(attrs={'rows':4, 'cols':45}),
            #'dob': forms.DateInput(format = ['%d/%m/%Y','%d-%m-%Y','%Y-%m-%d']),
            #'idissue': forms.DateInput(format = ['%d/%m/%Y','%d-%m-%Y','%Y-%m-%d']),
            #'idexpire': forms.DateInput(format['%d/%m/%Y','%d-%m-%Y','%Y-%m-%d']),
        }

    def clean_statement_check(self):
        check = self.cleaned_data['statement_check']
        if check==True:
            check = self.cleaned_data['statement_check']
        else:
            raise ValidationError('Beneficiary account statement must be checked before submission of cash incentive claim')
        # Always return a value to use as the new cleaned data, even if
        # this method didn't change it.
        return check

    def clean_letter_check(self):
        check = self.cleaned_data['letter_check']
        if check==True:
            check = self.cleaned_data['letter_check']
        else:
            raise ValidationError('Beneficiary\'s Letter of Incentive Claim must be obtained before submission of claim')
        # Always return a value to use as the new cleaned data, even if
        # this method didn't change it.
        return check

    def clean_document_check(self):
        check = self.cleaned_data['document_check']
        if check==True:
            check = self.cleaned_data['document_check']
        else:
            raise ValidationError("Remitter's documents must be checked before submission of cash incentive claim")
        # Always return a value to use as the new cleaned data, even if
        # this method didn't change it.
        return check

    def clean_doc_type(self):
        doc_type = self.cleaned_data['doc_type'].upper()

        # Always return a value to use as the new cleaned data, even if
        # this method didn't change it.
        return doc_type

    def clean_account_title(self):
        account_title = self.cleaned_data['account_title'].upper()

        # Always return a value to use as the new cleaned data, even if
        # this method didn't change it.
        return account_title

    def clean_sender_name(self):
        sender_name = self.cleaned_data['sender_name'].upper()

        # Always return a value to use as the new cleaned data, even if
        # this method didn't change it.
        return sender_name


    def clean(self):
        cleaned_data = super().clean()
        passport_issuing_country = cleaned_data.get("passport_issuing_country")
        visa_check = cleaned_data.get("visa_check")
        #if 'cash_incentive_status' in form.changed_data:
        if passport_issuing_country.name != 'BANGLADESH' and (visa_check==False or visa_check==None):
            raise forms.ValidationError("Claim cannot be submitted without obtaining \"NO Visa Required\" Documents for foreign passport holders")
        if passport_issuing_country.name == 'BANGLADESH' and visa_check!=None:
            raise forms.ValidationError(" \"NO Visa Required\" Documents field only required for foreign passport holders")
