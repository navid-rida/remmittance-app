#from django.forms.fields import InvalidJSONInput
from .models import Foreignbank, Remmit, ExchangeHouse, Branch, Receiver, Requestpay, Country,Booth, Claim, Encashment, Account
from django.forms import ModelForm
#from django.forms.models import formset_factory
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
###### Configuration ##################
from django.conf import settings

class RemmitForm(ModelForm):
    date_sending = forms.DateField(label="Date of Sending Remittance from Abroad", widget=forms.TextInput(attrs={'placeholder': 'dd/mm/yy'}), input_formats=['%d/%m/%Y','%d-%m-%Y','%Y-%m-%d'])

    class Meta:
        model = Remmit
        fields = ('exchange','rem_country','reference','sender','sender_gender','amount', 'currency','relationship', 'purpose','mariner_status','date_sending','sender_occupation', 'account', 'sender_bank')
        #widgets = {
            #'dob': forms.SelectDateWidget,
            #'cash_incentive_status': forms.RadioSelect,
            #'dob': forms.DateInput(format = ['%d/%m/%Y','%d-%m-%Y','%Y-%m-%d']),
            #'idissue': forms.DateInput(format = ['%d/%m/%Y','%d-%m-%Y','%Y-%m-%d']),
            #'idexpire': forms.DateInput(format['%d/%m/%Y','%d-%m-%Y','%Y-%m-%d']),
        #}

    def __init__(self, *args, **kwargs):
            self.request = kwargs.pop('request')
            self.receiver = kwargs.pop('receiver')
            super(RemmitForm, self).__init__(*args, **kwargs)
            self.fields['rem_country'].queryset = Country.objects.exclude(name="BANGLADESH")
            #self.fields['exchange'].queryset = ExchangeHouse.objects.exclude(name="MONEYGRAM")
            self.fields['account'].queryset = self.receiver.account_set.all()

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
        if date_sending < timezone.localtime().date() - timedelta(days=90):
            raise ValidationError('Validation error: date is too far away')
        if date_sending > timezone.localtime().date():
            raise ValidationError('Date Sending cannot be a future date')
        # Always return a value to use as the new cleaned data, even if
        # this method didn't change it.
        return date_sending

    def clean_currency(self):
        currency = self.cleaned_data['currency']
        exchange = self.cleaned_data['exchange']
        exchange_list = ['WESTERN UNION','XPRESS MONEY','RIA MONEY TRANSFER','PLACID EXPRESS','MONEYGRAM']
        if (exchange.name!='SWIFT' and exchange.name != 'CASH DEPOSIT') and (currency.name!='BANGLADESHI TAKA'):
            raise ValidationError('Only BDT can be selected for '+exchange.name )
        if (exchange.name=='SWIFT' or exchange.name == 'CASH DEPOSIT') and currency.name=='BANGLADESHI TAKA':
            raise ValidationError('Only FC can be selected for '+ exchange.name )
        # Always return a value to use as the new cleaned data, even if
        # this method didn't change it.
        return currency


    def clean(self):
        cleaned_data = super().clean()
        exchange = cleaned_data.get("exchange")
        reference = cleaned_data.get("reference")
        cash_incentive_status = cleaned_data.get("cash_incentive_status")
        sender_bank = cleaned_data.get("sender_bank")
        account = cleaned_data.get("account")
        rem_country = cleaned_data.get("rem_country")
        mariner_status = cleaned_data.get("mariner_status")
        
        #if 'cash_incentive_status' in form.changed_data:
        
        if exchange.name == 'WESTERN UNION':
            try:
                validate_western_code(reference)
            except ValidationError as err:
                self.add_error('reference',err)
        elif exchange.name == 'XPRESS MONEY':
            try:
                validate_xpress(reference)
            except ValidationError as err:
                self.add_error('reference',err)
        elif exchange.name == 'RIA MONEY TRANSFER':
            try:
                validate_ria(reference)
            except ValidationError as err:
                self.add_error('reference',err)
        elif exchange.name == 'PLACID EXPRESS':
            try:
                validate_placid(reference)
            except ValidationError as err:
                self.add_error('reference',err)
        elif exchange.name == 'MONEYGRAM':
            try:
                validate_moneygram(reference)
            except ValidationError as err:
                self.add_error('reference',err)
        elif exchange.name == 'PRABHU MONEY TRANSFER':
            try:
                prabhu_re(reference)
            except ValidationError as err:
                self.add_error('reference',err)
        elif exchange.name == 'MERCHANTRADE':
            try:
                merchantrade_re(reference)
                validate_merchantrade_ref(reference)
            except ValidationError as err:
                self.add_error('reference',err)
        elif exchange.name == 'NEC MONEY TRANSFER':
            try:
                validate_necmoney_ref(reference)
            except ValidationError as err:
                self.add_error('reference',err)
        elif exchange.name == 'NATIONAL EXCHANGE':
            try:
                validate_necitaly_ref(reference)
            except ValidationError as err:
                self.add_error('reference',err)
        elif exchange.name == 'CBL MONEY TRANSFER':
            try:
                validate_cbl_ref(reference)
            except ValidationError as err:
                self.add_error('reference',err)
        elif exchange.name == 'SWIFT':
            #if not receiver.ac_no:
                #self.add_error("Receiver must have an NRCB account for receiving remittance through SWIFT")
            if cash_incentive_status=='P':
                self.add_error('cash_incentive_status', "Cash Incentive against remittance received though SWIFT is not applicable before encashment in BDT")
            try:
                swift_re(reference)
            except ValidationError as err:
                self.add_error('reference',err)
            #if not self.request.user.has_perm('rem.can_add_swift_cash_deposit_remit'):
                #self.add_error('exchange', "SWIFT remittance can only be disbursed though ad branch user")
            if not sender_bank:
                self.add_error('sender_bank', "You must select a sender's Bank for SWIFT remittances")
            if not account:
                self.add_error('account', 'Benificiary account is mandatory for SWIFT remittances')
            if (sender_bank and rem_country) and sender_bank.country != rem_country:
                self.add_error('sender_bank', "\"Remittiting Country\" and \"Country of Sender's Bank\" mismatch")

        elif exchange.name == 'CASH DEPOSIT':
            #if not receiver.ac_no:
                #self.add_error("Receiver must have an NRCB account for receiving remittance through SWIFT")
            try:
                cash_deposit_reference_re(reference)
            except ValidationError as err:
                self.add_error('reference',err)
            if cash_incentive_status=='P' or cash_incentive_status=='U':
                self.add_error('cash_incentive_status', "Cash Incentive is not applicable for cash deposits")
            #if not self.request.user.has_perm('rem.can_add_swift_cash_deposit_remit'):
                #self.add_error('exchange', "Cash deposit remittance can only be disbursed though ad branches")
            if account:
                try:
                    nrbc_fc_acc(account.number)
                except ValidationError as err:
                    self.add_error('account',err)
            else:
                self.add_error('account', 'Benificiary account is mandatory for Cash deposit remittances')

        else:
            self.add_error('reference',"The reference number does not match with any known third party remittance services ")
        if sender_bank and exchange.name!='SWIFT':
            self.add_error('sender_bank',"Sender's Bank is applicable only for SWIFT remittances")
        if mariner_status == True and exchange.name!='SWIFT':
            self.add_error('mariner_status',"Mariner remittance is applicable only for SWIFT remittances")
        if exchange.name!='SWIFT' and exchange.name!='CASH DEPOSIT' and not self.request.user.has_perm('rem.add_third_party_remmit'):
            self.add_error('exchange', 'You do not have permissions to add third party exchange house remittance')
        if (exchange.name =='SWIFT' or exchange.name =='CASH DEPOSIT') and not self.request.user.has_perm('rem.can_add_swift_cash_deposit_remit'):
            self.add_error('exchange', 'You do not have permissions to add swift remittance')
        #form.add_error('reference', err)

        return cleaned_data


class RemittInfoForm(RemmitForm):
    screenshot = forms.ImageField(required=settings.IMAGE_UPLOAD_REQUIRED)
    reason_a = forms.CharField(label='Reason for not paying cash incentive', required=False, )
    PAYMENT= 'P'
    NONPAYMENT = 'U'
    NOTAPPLICABLE = 'NA'
    ENTRYCAT_CHOICES = (
        ('', '-----------'),
        (PAYMENT,'Pay Now'),
        (NONPAYMENT, 'Pay Later'),
        (NOTAPPLICABLE, 'Cash Incentive Not Applicable'),
        )
    entry_category = forms.ChoiceField(label='Cash Incentive',choices=ENTRYCAT_CHOICES, required=True)
    sender_bank = forms.ModelChoiceField(queryset=Foreignbank.objects.all(), required=False, label="Sender's Bank/ Ordering Institution", help_text="Ordering Institution: F52A for remittance through SWIFT. If not listed, you can add foreign bank")

    def __init__(self, *args, **kwargs):
        super(RemittInfoForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        #self.helper.render_unmentioned_fields= True
        self.helper.layout = Layout(
            'exchange',
            'sender_bank',
            'rem_country',
            'reference',
            'account',
            'sender',
            'sender_gender',
            'currency',
            'amount',
            'relationship', 
            'purpose',
            'mariner_status',
            Field('date_sending', css_class="date"),
            #'unpaid_cash_incentive_reason', 
            #'cash_incentive_status',
            'sender_occupation',
            'screenshot',
            'entry_category',
            'reason_a',
            Submit('submit', 'CREATE')
        )

    """def clean_reason_a(self):
        unpaid_cash_incentive_reason = self.cleaned_data['reason_a']
        cash_incentive_status = self.cleaned_data['entry_category']
        if cash_incentive_status == 'U' and unpaid_cash_incentive_reason==None:
            raise ValidationError('Reason is required if cash incentive status is unpaid')
        # Always return a value to use as the new cleaned data, even if
        # this method didn't change it.
        return unpaid_cash_incentive_reason"""

    def clean_entry_category(self):
        cash_incentive_status = self.cleaned_data['entry_category']
        exchange = self.cleaned_data['exchange']
        if 'entry_category' in self.changed_data and cash_incentive_status=='U' and self.fields['entry_category'].initial=="":
            raise ValidationError('Validation error: A remittance cannot be marked unpaid once it is paid')
        if cash_incentive_status=='P' and exchange.name=='SWIFT':
            raise ValidationError('Cash Incentive against remittance received though SWIFT is not applicable before encashment in BDT')
        if (cash_incentive_status=='P' or cash_incentive_status == 'U') and exchange.name=='CASH DEPOSIT':
            raise ValidationError('Cash Incentive is not applicable in Cash deposit')
        # Always return a value to use as the new cleaned data, even if
        # this method didn't change it.
        return cash_incentive_status

    def clean(self):
        cleaned_data = super().clean()
        #exchange = cleaned_data.get("exchange")
        #reference = cleaned_data.get("reference")
        cash_incentive_status = cleaned_data.get("entry_category")
        unpaid_cash_incentive_reason = cleaned_data.get("reason_a")
        #if 'cash_incentive_status' in form.changed_data:
        #if self.has_changed() and 'entry_category' in self.changed_data:
           # self.add_error('entry_category','Payment status cannot be changed while updating remittane information')
        if cash_incentive_status == 'U' and unpaid_cash_incentive_reason=="":
            msg = 'Reason is required if cash incentive status is unpaid'
            self.add_error('reason_a', msg)
        
    
    def save(self, commit=True):
        remit = super(RemittInfoForm, self).save(commit=False)
        #set some other attrs on user here ...
        remit._reason_a = self.cleaned_data['reason_a']
        remit.unpaid_cash_incentive_reason = self.cleaned_data['reason_a']
        remit._entry_cat = self.cleaned_data['entry_category']
        remit.cash_incentive_status = self.cleaned_data['entry_category']
        #user._other = 'other'
        if commit:
          remit.save()

        return remit


class EncashmentForm(ModelForm):
    #date_sending = forms.DateField(widget=forms.TextInput(attrs={'placeholder': 'dd/mm/yy'}), input_formats=['%d/%m/%Y','%d-%m-%Y','%Y-%m-%d'])
    #account = forms.ModelChoiceField(queryset=ExchangeHouse.objects.all(),required=False)

    class Meta:
        model = Encashment
        fields = ('amount','rate', 'cashin_category', 'reason', 'account')
        #widgets = {
            #'dob': forms.SelectDateWidget,
            #'cash_incentive_status': forms.RadioSelect,
            #'dob': forms.DateInput(format = ['%d/%m/%Y','%d-%m-%Y','%Y-%m-%d']),
            #'idissue': forms.DateInput(format = ['%d/%m/%Y','%d-%m-%Y','%Y-%m-%d']),
            #'idexpire': forms.DateInput(format['%d/%m/%Y','%d-%m-%Y','%Y-%m-%d']),
        #}

    def __init__(self, *args, **kwargs):
        receiver_id=kwargs.pop('pk')
        rem = Remmit.objects.get(pk=receiver_id)
        super(EncashmentForm, self).__init__(*args, **kwargs)
        self.fields['account'].queryset = Account.objects.filter(receiver=rem.receiver)
        self.helper = FormHelper(self)
        #self.helper.render_unmentioned_fields= True
        self.helper.layout = Layout(
            'amount',
            'rate',
            'cashin_category',
            'reason',
            'account',
            Submit('submit', 'Encash')
        )


    def clean_reason(self):
        unpaid_cash_incentive_reason = self.cleaned_data['reason']
        cashin_category  = self.cleaned_data['cashin_category'] if 'cashin_category' in self.cleaned_data else None
        if cashin_category != 'P' and unpaid_cash_incentive_reason==None:
            raise ValidationError('Reason is required if cash incentive status is unpaid')
        # Always return a value to use as the new cleaned data, even if
        # this method didn't change it.
        return unpaid_cash_incentive_reason

class AccountForm(ModelForm):
    #date_sending = forms.DateField(widget=forms.TextInput(attrs={'placeholder': 'dd/mm/yy'}), input_formats=['%d/%m/%Y','%d-%m-%Y','%Y-%m-%d'])

    class Meta:
        model = Account
        fields = ('number','title', 'branch', 'booth')
        #widgets = {
            #'dob': forms.SelectDateWidget,
            #'cash_incentive_status': forms.RadioSelect,
            #'dob': forms.DateInput(format = ['%d/%m/%Y','%d-%m-%Y','%Y-%m-%d']),
            #'idissue': forms.DateInput(format = ['%d/%m/%Y','%d-%m-%Y','%Y-%m-%d']),
            #'idexpire': forms.DateInput(format['%d/%m/%Y','%d-%m-%Y','%Y-%m-%d']),
        #}

    def __init__(self, *args, **kwargs):
        super(AccountForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        #self.helper.render_unmentioned_fields= True
        self.helper.layout = Layout(
            'number',
            'title',
            'branch',
            'booth',
            Submit('submit', 'Create')
        )


    def clean_reason(self):
        unpaid_cash_incentive_reason = self.cleaned_data['reason']
        cashin_category  = self.cleaned_data['cashin_category'] if 'cashin_category' in self.cleaned_data else None
        if cashin_category != 'P' and unpaid_cash_incentive_reason==None:
            raise ValidationError('Reason is required if cash incentive status is unpaid')
        # Always return a value to use as the new cleaned data, even if
        # this method didn't change it.
        return unpaid_cash_incentive_reason

#AccountFormset = formset_factory(AccountForm)

class ForeignBankForm(ModelForm):
    #date_sending = forms.DateField(widget=forms.TextInput(attrs={'placeholder': 'dd/mm/yy'}), input_formats=['%d/%m/%Y','%d-%m-%Y','%Y-%m-%d'])

    class Meta:
        model = Foreignbank
        fields = ('name','swift_bic', 'country')
        #widgets = {
            #'dob': forms.SelectDateWidget,
            #'cash_incentive_status': forms.RadioSelect,
            #'dob': forms.DateInput(format = ['%d/%m/%Y','%d-%m-%Y','%Y-%m-%d']),
            #'idissue': forms.DateInput(format = ['%d/%m/%Y','%d-%m-%Y','%Y-%m-%d']),
            #'idexpire': forms.DateInput(format['%d/%m/%Y','%d-%m-%Y','%Y-%m-%d']),
        #}

    def __init__(self, *args, **kwargs):
        super(ForeignBankForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        #self.helper.render_unmentioned_fields= True
        self.helper.layout = Layout(
            'name',
            'swift_bic',
            'country',
            Submit('submit', 'Create')
        )


    """def clean_reason(self):
        unpaid_cash_incentive_reason = self.cleaned_data['reason']
        cashin_category  = self.cleaned_data['cashin_category'] if 'cashin_category' in self.cleaned_data else None
        if cashin_category != 'P' and unpaid_cash_incentive_reason==None:
            raise ValidationError('Reason is required if cash incentive status is unpaid')
        # Always return a value to use as the new cleaned data, even if
        # this method didn't change it.
        return unpaid_cash_incentive_reason"""

class ReceiverForm(ModelForm):
    dob = forms.DateField(widget=forms.TextInput(attrs={'placeholder': 'dd/mm/yy'}), label="Date of Birth",input_formats=['%d/%m/%Y','%d-%m-%Y','%Y-%m-%d'])
    idissue = forms.DateField(widget=forms.TextInput(attrs={'placeholder': 'dd/mm/yy'}), label="ID Issue Date",input_formats=['%d/%m/%Y','%d-%m-%Y','%Y-%m-%d'], required=False)
    idexpire = forms.DateField(widget=forms.TextInput(attrs={'placeholder': 'dd/mm/yy'}),label="ID Expiry date",input_formats=['%d/%m/%Y','%d-%m-%Y','%Y-%m-%d'], required=False)
    number = forms.CharField(label="Account Number (15 Digit)", max_length=15, validators=[nrbc_acc], help_text = "As per F 59 of MT103 for remittance received through SWIFT", required=False)
    title = forms.CharField(label="Account Title", max_length=100, required=False, )
    branch = forms.ModelChoiceField(label='Account Branch', queryset=Branch.objects.all(),required=False)
    booth = forms.ModelChoiceField(label='Account Sub-branch', queryset=Booth.objects.all(),required=False)
    #accounts = AccountFormset()

    class Meta:
        model = Receiver
        exclude = ['created_by','ac_no']
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
            'number',
            'title',
            'branch',
            'booth',
            Submit('submit', 'CREATE')
        )

    def clean_idno(self):
        idno = self.cleaned_data['idno']
        idtype = self.cleaned_data['idtype']
        #idissue = self.cleaned_data['idissue']
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

    """def clean_idexpire(self):
        idexpire = self.cleaned_data['idexpire']
        idissue = self.cleaned_data['idissue']
        idtype = self.cleaned_data['idtype']
        #idtype = self.cleaned_data['idtype']
        
       
        # Always return a value to use as the new cleaned data, even if
        # this method didn't change it.
        return idexpire"""

    """def clean_idissue(self):
        idissue = self.cleaned_data['idissue']
        idtype = self.cleaned_data['idtype']
        #idtype = self.cleaned_data['idtype']
        if idissue and idissue > timezone.localtime().date():
            raise ValidationError('ID Issue date cannot be a future date')
        if idtype == 'PASSPORT' and idissue:
            raise ValidationError('ID Issue date is mandatory for Passports')
        # Always return a value to use as the new cleaned data, even if
        # this method didn't change it.
        return idissue"""

    

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
        number = cleaned_data.get("number")
        branch = cleaned_data.get("branch")
        booth = cleaned_data.get("booth")
        idissue = cleaned_data.get("idissue")
        idtype = cleaned_data.get("idtype")
        idexpire = cleaned_data.get("idexpire")
        br_prefix = number[0:4] if number else None
        #unpaid_cash_incentive_reason = cleaned_data.get("unpaid_cash_incentive_reason")
        #if 'cash_incentive_status' in form.changed_data:
        if idissue and idissue > timezone.localtime().date():
            raise ValidationError('ID Issue date cannot be a future date')
        if idtype == 'PASSPORT' and not (idissue and idexpire):
            raise ValidationError('ID Issue date/ Expiry Date is mandatory for Passports')
        if idissue and idexpire and idissue >= idexpire:
            self.add_error('idexpire','ID Expiry Date cannot be on or before issue date')
        if idtype == 'PASSPORT' and idexpire > idissue + timezone.timedelta(days=10*365+10):
            self.add_error('idexpire','Passport expiry period cannot be more than ten years')
        if gender=='F' and (father==None and spouse==None):
             raise forms.ValidationError(
                    "Either father name or husbands name is required"
                )
        if number and not (branch or booth):
            self.add_error('number','Branch or booth cannot be left blank for accounts')
        if booth:
            if br_prefix!=booth.code:
                self.add_error('number','Sub-branch prefix mismatch')
            if booth.branch!=branch:
                self.add_error('booth','Branch/Sub-branch mismatch')
        else:
            if br_prefix and br_prefix!=branch.code:
                self.add_error('number','Branch prefix mismatch')
        

class ReceiverSearchForm(forms.Form):
    #cell = forms.CharField(label="Enter Customer's Cell No.", validators=[validate_mobile])
    identification = forms.CharField(label="Enter NID/Passport/ Birth Certificate No.")

class ReceiverChangeForm(forms.Form):
    reference = forms.CharField(label="Referene No./PIN/MTCN", max_length=16)
    identification = forms.CharField(label="Enter NID/Passport/ Birth Certificate No. of New Receiver", max_length=17)

    def __init__(self, *args, **kwargs):
        super(ReceiverChangeForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        #self.helper.render_unmentioned_fields= True
        self.helper.layout = Layout(
            'reference',
            'identification',
            Submit('submit', 'Change Receiver')
        )

class MultipleSearchForm(forms.Form):
    #cell = forms.CharField(label="Enter Customer's Cell No.", validators=[validate_mobile])
    keyword = forms.CharField(label="Enter reference number, name or phone no")

    def __init__(self, *args, **kwargs):
        super(MultipleSearchForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        #self.helper.render_unmentioned_fields= True
        self.helper.layout = Layout(
            Field('keyword', css_class="form-control form-control-dark w-100", type="text", placeholder="Search", aria_label="Search"),
            #'unpaid_cash_incentive_reason', 
            #'cash_incentive_status',
            Submit('submit', 'CREATE')
        )


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.add_input(Submit('submit', 'Submit'))
        
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
