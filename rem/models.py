#from tkinter.tix import Tree
from locale import currency
from django.db import models
from decimal import Decimal
from django.urls import reverse_lazy,reverse
#from datetime import date
from django.core.exceptions import ValidationError
from django.db.models.fields.related import ForeignKey
from .validators import validate_expire_date, validate_neg, validate_post_date, validate_mobile, numeric, name, alpha, alpha_num, western_union, nrbc_acc, swift_bic
from django.core.validators import RegexValidator
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.safestring import mark_safe
import datetime
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
import pandas as pd
from rem.DataModels import cash_incentive_df, filter_remittance, filter_claim
########################## aggregate functions ###############################
from django.db.models import Sum, Q
################# import for validation errrors ##############################
from django.utils.translation import gettext_lazy as _

####################### Rules ################################
import rem.rule_set
import rules
from rules.contrib.models import RulesModel
################################### Other app models ##################
from schedules.models import District, Currency, Bank, Rate

######################### Custom Managers ###############################
# Create your models here.


class Branch(models.Model):
    name = models.CharField("Name of The branch", max_length=20,default='Principal')
    code = models.CharField("Branch Code", validators=[numeric], max_length=4,default='0101', unique=True)
    ad_fi_code = models.CharField("AD FI Code", validators=[numeric], max_length=4, null=True, blank=True, unique=True)
    district = models.ForeignKey(District, on_delete=models.CASCADE, verbose_name='District', null=True)
    address = models.TextField("Address of the branch")

    def __str__(self):
        return self.name

    def employee_count(self, active_status=None):
        count = 0
        if active_status==True:
            count = self.employee_set.filter(user__is_active=active_status).count()
        elif active_status==False:
            count = self.employee_set.filter(user__is_active=active_status).count()
        else:
            count = self.employee_set.count()
        return count

    def total_sum_count(self, year=None, month=None, start_date=None, end_date= None, exchange_house=None, BranchBooth=None):
        p = Payment.objects.filter(requestpay__remittance__branch=self)
        if BranchBooth=='branch':
            p = p.filter(requestpay__remittance__booth__isnull=True)
        if year and not month:
            p = p.filter(date_settle__year=year)
        elif year and month:
            p = p.filter(date_settle__year=year).filter(date_settle__month=month)
        elif start_date and end_date:
            p = p.filter(date_settle__date__range=(start_date,end_date))
        else:
            pass
        if exchange_house:
            p = p.filter(requestpay__remittance__exchange=exchange_house)
        sum = p.aggregate(sum = Sum('requestpay__remittance__amount'))
        count = p.count()
        sum = sum['sum'] if sum['sum'] else 0
        return sum, count

    def branch_total_month(self, year):
        p = Payment.objects.filter(requestpay__remittance__branch=self).filter(date_settle__year=year)


    #def branch_total(year=None,month=None,date=None,exchan_house=None,start_date=None,end_date=None):

class Booth(models.Model):
    name = models.CharField("Name of the Sub-branch", max_length=20)
    code = models.CharField("Sub-branch Code", validators=[numeric], max_length=4, unique=True)
    address = models.TextField("Address of the Sub-branch")
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, verbose_name='Branch Attached')

    def __str__(self):
        return self.name

    def employee_count(self, active_status=None):
        count = 0
        if active_status==True:
            count = self.employee_set.filter(user__is_active=active_status).count()
        elif active_status==False:
            count = self.employee_set.filter(user__is_active=active_status).count()
        else:
            count = self.employee_set.count()
        return count

    def is_under_branch(self,branch):
        return self.branch == branch

    def total_sum_count(self, year=None, month=None, start_date=None, end_date= None, exchange_house=None, BranchBooth=None):
        p = Payment.objects.all()
        if year and not month:
            p = p.filter(requestpay__remittance__booth=self).filter(date_settle__year=year)
        elif year and month:
            p = p.filter(requestpay__remittance__booth=self).filter(date_settle__year=year).filter(date_settle__month=month)
        elif start_date and end_date:
            p = p.filter(requestpay__remittance__booth=self).filter(date_settle__date__range=(start_date,end_date))
        else:
            p = p.filter(requestpay__remittance__booth=self)
        if exchange_house:
            p = p.filter(requestpay__remittance__exchange=exchange_house)
        sum = p.aggregate(sum = Sum('requestpay__remittance__amount'))
        count = p.count()
        sum = sum['sum'] if sum['sum'] else 0
        return Decimal(sum), count

class Country(models.Model):
    name = models.CharField("Remitting Country", max_length=50)
    code = models.CharField("Country code", max_length=20)

    def __str__(self):
        return self.name


class Foreignbank(models.Model):
    name = models.CharField('Name of the FI', max_length=60, unique=True, help_text='Ordering Institution: F52A for remittance through SWIFT')
    swift_bic = models.CharField('SWIFT BIC', max_length=11, unique=True, validators=[swift_bic,], help_text='Ordering Institution\'s SWIFT BIC: F52A for remittance through SWIFT')
    country = models.ForeignKey(Country, on_delete=models.PROTECT, verbose_name='Country of the Bank')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    date_create = models.DateTimeField("Date of Creation", auto_now_add=True)

    def __str__(self):
        return self.name+" "+self.swift_bic


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, verbose_name='Branch of the Employee')
    booth = models.ForeignKey(Booth, on_delete=models.CASCADE, verbose_name='Sub-branch of the Employee', null=True, blank=True)
    cell = models.CharField("Cell number of Employee", validators=[validate_mobile], max_length=14)
    def __str__(self):
        return self.user.get_full_name()

    def check_group(self, group_name):
        if self.user.groups.filter(name=group_name).exists():
            return True
        else:
            return False

    def check_user_quota_available(self):
        total_employee = self.branch.employee_count()
        if self.branch.name == 'Head office':
            maximum_allowed_user=settings.MAXIMUM_USER_HEAD_OFFICE
        else:
            maximum_allowed_user=settings.MAXIMUM_USER_PER_BRANCH
        if maximum_allowed_user > total_employee:
            return True
        else:
            return False

    def get_related_remittance(self, start_date=None, end_date= None, branch= None, booth= None, exchange_house=None, keyword=None, BranchBooth=None):
        query_set = Remmit.objects.all()
        if self.user.has_perm('rem.view_all_remitt'):
            rem = filter_remittance(query_set = query_set, start_date=start_date, end_date= end_date, branch= branch, booth= booth, exchange_house=exchange_house,keyword=keyword, BranchBooth=BranchBooth)
        elif self.user.has_perm('rem.view_branch_remitt'):
            rem = filter_remittance(query_set = query_set, start_date=start_date, end_date= end_date, branch= self.branch, booth= booth, exchange_house=exchange_house,keyword=keyword, BranchBooth=BranchBooth)
        elif self.user.has_perm('rem.view_booth_remitt'):
            rem = filter_remittance(query_set = query_set, start_date=start_date, end_date= end_date, booth= self.booth, exchange_house=exchange_house,keyword=keyword)
        else:
            if self.booth:
                query_set = self.user.remmit_set.filter(booth=self.booth)
                rem = filter_remittance(query_set = query_set, start_date=start_date, end_date= end_date, exchange_house=exchange_house,keyword=keyword)
            else:
                query_set = self.user.remmit_set.filter(branch=self.branch)
                rem = filter_remittance(query_set = query_set, start_date=start_date, end_date= end_date, booth= booth, exchange_house=exchange_house,keyword=keyword)
        return rem

    def get_related_claim(self, start_date=None, end_date= None, branch= None, booth=None):
        query_set = Claim.objects.all()
        if self.user.has_perm('rem.view_all_remitt'):
            claims = filter_claim(query_set = query_set, start_date=start_date, end_date= end_date, branch= branch, booth = booth)
        elif self.user.has_perm('rem.view_branch_remitt'):
            claims = filter_claim(query_set = query_set, start_date=start_date, end_date= end_date, branch= self.branch)
        elif self.user.has_perm('rem.view_booth_remitt'):
            claims = filter_claim(query_set = query_set, start_date=start_date, end_date= end_date, booth= self.booth)
        else:
            if self.booth:
                query_set = self.user.remmit_set.filter(booth=self.booth)
                claims = filter_claim(query_set = query_set, start_date=start_date, end_date= end_date)
            else:
                query_set = self.user.remmit_set.filter(branch=self.branch)
                claims = filter_claim(query_set = query_set, start_date=start_date, end_date= end_date)
        return claims

    """def clean(self):
        # Don't allow draft entries to have a pub_date.
        if self.id and self.check_user_quota_available() == False:
            raise ValidationError(_('Maximum User Limit exceeded'))

    def save(self, *args, **kwargs):
        self.full_clean()
        return super(Employee, self).save(*args, **kwargs)"""

"""@receiver(post_save, sender=User)
def update_user_employee(sender, instance, created, **kwargs):
    if created:
        Employee.objects.create(user=instance, branch=None, cell=None)
    instance.employee.save()"""



class Receiver(models.Model):
    name = models.CharField("Name of Receiver", validators=[name], max_length=100)
    MALE= 'M'
    FEMALE = 'F'
    OTHER = 'O'
    GENDER_CHOICES = (
        (MALE,'MALE'),
        (FEMALE, 'FEMALE'),
        (OTHER, 'Other'),
        )
    gender=models.CharField("Gender of Receiver",max_length=1, choices=GENDER_CHOICES)
    father_name = models.CharField("Father's name of Receiver", max_length=100, null=True, blank=True)
    mother_name = models.CharField("Mother's Name of Receiver", max_length=100)
    spouse_name = models.CharField("Spouse name",  max_length=100, null=True, blank=True)
    SERVICE= 'S'
    BUSINESS = 'B'
    OTHER = 'O'
    OCCUPATION_CHOICES = (
        (SERVICE,'SERVICE'),
        (BUSINESS, 'BUSINESS'),
        (OTHER, 'OTHER'),
        )
    profession = models.CharField("Profession", max_length=100, choices=OCCUPATION_CHOICES)
    nationality = models.ForeignKey(Country,on_delete=models.CASCADE, verbose_name='Nationality',  default=Country.objects.get(name='BANGLADESH').id)
    ac_no = models.CharField("Account Number of the receiver (If any)", validators=[nrbc_acc], max_length=15, null=True, blank=True)
    address = models.TextField("Address of Receiver")
    dob = models.DateField("Date of Birth of Receiver")
    cell = models.CharField("Cell number of Receiver", validators=[validate_mobile], max_length=14, unique=True)
    NID= 'NID'
    PASSPORT = 'PASSPORT'
    BC = 'BC'
    DL = 'DL'
    STATUS_CHOICES = (
        (NID,'National ID'),
        (PASSPORT, 'Passport'),
        (BC, 'Birth Regestration Certificate'),
        (DL, 'Driving License'),
        )
    idtype=models.CharField("Type of Identification",max_length=8, choices=STATUS_CHOICES, default=NID)
    idissue = models.DateField("Issue date of Identification Document", null=True)
    idexpire = models.DateField("Expiry date of Identification Document", null=True)
    idno = models.CharField("ID Number", max_length=17, unique=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Benificiary of Remittance"
        #constraints = [
        #    models.CheckConstraint(check=models.Q(nationality__name='BANGLADESH'), name='nationality_is_bangladeshi'),
        #]


    def __str__(self):
        return self.name

    def get_first_remit_user(self):
        remittance = self.remmit_set.order_by('date_create').first()
        if remittance:
            return remittance.created_by
        else:
            return False

    def set_first_remit_user_as_creator(self):
        user = self.get_first_remit_user()
        if user:
            self.created_by = user
            return self.save()
        else:
            return False

    def get_nid(self):
        """Returns NID number of receiver.
        Returns False if id is not NID"""
        if self.idtype=='NID':
            return self.idno
        else:
            return None

    def get_passport_no(self):
        """Returns Passport number of receiver.
        Returns False if id is not passport"""
        if self.idtype=='PASSPORT':
            return self.idno
        else:
            return None

    def check_incomplete_info(self):
        if self.father_name=='N/A' or self.mother_name=='N/A' or self.spouse_name=='N/A' or self.profession == 'N/A' or self.gender=='O':
            return True
        else:
            return False

    def check_fc_account(self):
        if self.ac_no[0] == '2':
            return True
        else:
            False


class ReceiverUpdateHistory(models.Model):
    receiver=models.ForeignKey(Receiver, on_delete=models.CASCADE, verbose_name= "Receiver")
    datecreate = models.DateTimeField("Date of Editing", auto_now_add=True)
    createdby = models.ForeignKey(User, on_delete=models.PROTECT)
    ip = models.GenericIPAddressField("User IP Address")

class Account(models.Model):
    receiver = models.ForeignKey(Receiver, on_delete=models.PROTECT, verbose_name="Receiver")
    number = models.CharField("Account Number (15 Digit)", max_length=15, validators=[nrbc_acc], unique=True)
    title = models.CharField("Account Title", max_length=100)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    booth = models.ForeignKey(Booth, on_delete=models.CASCADE, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    date_create = models.DateTimeField("Date of Creation", auto_now_add=True)

    def __str__(self):
        return self.number+" "+self.title
    

    def clean(self):
        br_prefix = self.number[0:4]
        if self.booth:
            if br_prefix!=self.booth.code:
                raise ValidationError({'number': _('Sub-branch prefix mismatch')})
            if self.booth.branch!=self.branch:
                raise ValidationError({'booth': _('Branch/Sub-branch mismatch')})
        else:
            if br_prefix!=self.branch.code:
                raise ValidationError({'number': _('Branch prefix mismatch')})
        
class ExchangeHouse(models.Model):
    name = models.CharField("Name of Exchange House", max_length=30)
    gl_no = models.CharField("GL Head of Exchange House", max_length=15,  validators=[numeric])
    gl_key = models.CharField("GL Key of Exchange House", max_length=11,  validators=[numeric])
    gl_key_name = models.CharField("Name of Exchange House GL Key Head", max_length=50)
    cash_incentive_gl_no = models.CharField("GL Head of Cash Incentive distribution", max_length=15,  validators=[numeric])
    cash_incentive_gl_key = models.CharField("GL Key of Cash Incentive", max_length=11,  validators=[numeric])
    cash_incentive_gl_key_name = models.CharField("Name of Cash incentive GL Key Head", max_length=50)
    ac_no = models.CharField("Account no./ GL No. of Exchange House", max_length=15,  validators=[numeric])
    ac_no_branch = models.ForeignKey(Branch,on_delete=models.CASCADE, verbose_name="Branch of CD Account/ GL")
    verbose_name = models.CharField("Full Name of the Exchangehouse", max_length= 100)

    def __str__(self):
        return self.name

fbank_url = reverse_lazy('fbank-create')

class Remmit(models.Model):
    exchange = models.ForeignKey(ExchangeHouse,on_delete=models.CASCADE, verbose_name='Channel of Remittance')
    #ordering_bank_name = models.CharField('F50K: Name of Ordering Institution', max_length=60, null=True,)
    #ordering_bank_swift = models.CharField('F50K: SWIFT BIC of Ordering Institution', max_length=11, null=True,)
    currency = models.ForeignKey(Currency,on_delete=models.CASCADE, verbose_name='Currency of Remittance', default=Currency.objects.get(name='BANGLADESHI TAKA').id)
    rem_country = models.ForeignKey(Country,on_delete=models.CASCADE, verbose_name='Remitting Country')
    sender = models.CharField("Name of Remitter", validators=[name], max_length=50)
    SERVICE= 'S'
    BUSINESS = 'B'
    OTHER = 'O'
    OCCUPATION_CHOICES = (
        (SERVICE,'SERVICE'),
        (BUSINESS, 'BUSINESS'),
        (OTHER, 'OTHER'),
        )
    sender_occupation = models.CharField("Occupation of Remitter", help_text="Service/ Business etc.",choices=OCCUPATION_CHOICES, validators=[alpha], max_length=50)
    MALE= 'M'
    FEMALE = 'F'
    OTHER = 'O'
    GENDER_CHOICES = (
        (MALE,'MALE'),
        (FEMALE, 'FEMALE'),
        (OTHER, 'Other'),
        )
    sender_gender=models.CharField("Gender of the Remitter",max_length=1, choices=GENDER_CHOICES)

    FAMILY='FM',
    FRIEND = 'FR',
    BUSINEESS_ASSOCIATE = 'BA',
    CLIENT='CL',
    EMPLOYEE ='EM',
    EMPLOYER ='ER',
    ACQUAINTANCE ='AC'

    RELATIONSHIP_CHOICES = (
        ('FM','Family'),
        ('FR','Friend'),
        ('BA','Business Associate'),
        ('CL','Client'),
        ('EM', 'Employee'),
        ('ER', 'Employer'),
        ('AC','Acquaintance'),
        ('SL','Self'),
    )

    relationship = models.CharField("Benificiary\'s relationship to Sender", max_length=50, null=True, choices = RELATIONSHIP_CHOICES)
    purpose = models.CharField("Purpose of Transaction",max_length=50, null=True)
    BOOL_CHOICES = ((True, 'Yes'), (False, 'No'))
    mariner_status = models.BooleanField("Mariner/ Cabin Crew Remittance?",choices=BOOL_CHOICES, help_text="Mark yes if the remittance remitted by Foreign Shipping Lines/ Airlines/ UN or UN Bodies/ Foreign Missions")
    PAID= 'P'
    #HELD = 'H'
    UNPAID = 'U'
    NOTAPPlICABLE='NA'
    CASHINC_CHOICES = (
        (PAID,'Pay Now'),
        #(HELD, 'Held'),
        (UNPAID, 'Pay Later'),
        (NOTAPPlICABLE, 'Not Applicable')
        )
    cash_incentive_status = models.CharField("Cash Incentive Status", choices=CASHINC_CHOICES, max_length=2, )
    unpaid_cash_incentive_reason = models.CharField("Reason for not paying cash incentive", max_length=50, null=True, blank=True, help_text="This field is mandatory if you mark cash incentive as unpaid")
    receiver = models.ForeignKey(Receiver, on_delete=models.PROTECT, verbose_name="Receiver")
    amount = models.DecimalField("Amount of Remittance",max_digits=20,decimal_places=2, validators=[validate_neg], help_text="Required documents must be collected and retained for paying inentive against Remittances valuing more than BDT 5,00,000.00 or USD 5,000.00 or equivalent FC")
    cash_incentive_amount = models.DecimalField("Amount of Cash Incentive",max_digits=20,decimal_places=2, validators=[validate_neg])
    account = models.ForeignKey(Account,verbose_name='Account of Benificiary', on_delete=models.PROTECT, null=True, blank = True)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    booth = models.ForeignKey(Booth, on_delete=models.CASCADE, null=True, blank=True)
    date_sending = models.DateField("Date of Sending Remittance from Abroad")
    date_cash_incentive_paid = models.DateTimeField("Date of Cash Incentive payment", null=True, blank= True)
    date_cash_incentive_settlement = models.DateField("Date of Cash Incentive Settlement", null=True, blank= True)
    date_create = models.DateTimeField("Date of posting", auto_now_add=True)
    date_edited = models.DateTimeField("Date of last modified", auto_now=True)
    reference = models.CharField("Referene No./PIN/MTCN", help_text='Referene No./PIN/MTCN/ For SWIFT - Sender\'s reference: F20A, <br> For Cash FC Deposit Remittance: C[BRANCH CODE]-YYYY-MM-DD-[Serial No (2 Digit)] e.g. C0101-2022-16-05-01', max_length=20, unique=True)
    screenshot = models.ImageField("Agent Copy", default = 'images/None/no-img.jpg')
    sender_bank = models.ForeignKey(Foreignbank, on_delete=models.CASCADE, verbose_name="Sender's Bank/ Ordering Institution", help_text="Ordering Institution: F52A for remittance through SWIFT. If not listed, you can add foreign bank", null=True, blank=True)
    #sender_bank = models.ForeignKey(Bank, on_delete=models.CASCADE, verbose_name="Sender's Bank/ Ordering Institution", null=True, blank=True, help_text='Ordering Institution: F52A for remittance through SWIFT')
    #sender_bank_swift = models.CharField("Sender's Bank's/ Ordering Institution's SWIFT BIC", max_length=11, validators=[swift_bic,], null=True, blank=True, help_text='Ordering Institution\'s SWIFT BIC: F52A for remittance through SWIFT')
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    edited_by = models.ForeignKey(User, on_delete=models.PROTECT, null=True, related_name='editors')
    #REVIEW= 'RV'
    #REJECTED = 'RJ'
    #PAID = 'PD'
    """STATUS_CHOICES = (
        (REVIEW,'Request to be Processed'),
        (REJECTED, 'Request Rejected'),
        (PAID, 'Amount Payable to Customer'),
        )
    status=models.CharField("Request Status",max_length=2, choices=STATUS_CHOICES, default=REVIEW)"""

    class Meta:
        verbose_name = "Remittance"
        #rules_permissions = {
           # "add" : rules.add_remit,
           # "change" : rules.change_remmit,
           # "read" : rem.rule_set.is_same_branch_user,
           # "delete" : rules.is_superuser,
         #}\
        #permissions = 
        """constraints = [
            models.CheckConstraint(check=models.Q)
        ]"""

    def __str__(self):
        return self.reference+" on "+self.branch.name



    #################### Encashment Related Methods ######################


    def get_total_encashment_value(self):
        total_encashment = self.encashment_set.aggregate(sum=Sum('amount'))
        if total_encashment['sum']:
            return total_encashment['sum']
        else:
            return 0
    
    def get_encashment_room(self):
        ### return available limit for encashment 
        room = self.amount - self.get_total_encashment_value()
        if room>0:
            return room
        else:
            return 0
    ##################################################
    def clean(self):
        if self.cash_incentive_status=='U' and self.date_cash_incentive_paid is not None:
            raise ValidationError({'cash_incentive_status': _('A remittance cannot be marked unpaid once it is paid')})
        if self.booth and self.booth.branch.code != self.branch.code:
            raise ValidationError(_('Branch/ Sub-branch Mismatch'))
        #if self.exchange.name=='SWIFT' and self.currency.name=='BANGLADESHI TAKA':
            #raise ValidationError(_('Currency must be FC for SWIFT or Cash Remttance'))
        #if (not self.branch.ad_fi_code) and self.exchange.name=='SWIFT':
            #raise ValidationError(_('SWIFT remittance can only be posted by AD branches'))

        #if self.exchange.name == 'SWIFT' and (not self.receiver.ac_no):
            #raise ValidationError(_('Receiver acccount required'))

    def get_completed_payment(self):
        r = self.requestpay_set.order_by('datecreate',).last()
        if r.payment:
            return r.payment
        else:
            return False

    def check_unpaid_cash_incentive(self):
        #This one checks the cash incentive in remmit table
        if self.cash_incentive_status=='U' and self.date_cash_incentive_paid is None and self.date_create.date()>datetime.date(2019,6,30):
            return True
        else:
            return False

    def check_if_cash_incentive_paid(self):
        #This one checks the cash incentive in seperate CashIncentive Table
        q = self.cashincentive_set.all()
        for c in q:
            if c.check_if_paid():
                return True
        return False

    def get_paid_cash_incentives(self):
        return self.cashincentive_set.filter(entry_category='P')
    
    def get_paid_cash_incentives_number(self):
        return self.cashincentive_set.filter(entry_category='P').count()


    def pay_previously_unpaid_cash_incentive(self):
        if self.check_unpaid_cash_incentive():
            self._entry_cat='P'
            self.cash_incentive_status='P'
            self.date_cash_incentive_paid=timezone.now()
            self.cash_incentive_amount=self.amount*Decimal(0.025)
            self.save()
            self.refresh_from_db()
            return self
        else:
            return False

    def cash_incentive_is_settled(self):
        """Checks whether the payment cash incentive is settled.
            Returns True if settled else False"""
        if self.cash_incentive_status=='P' and self.date_cash_incentive_paid and self.date_cash_incentive_settlement:
            return True
        else:
            return False

    def settle_cash_incentive(self, date_settle= timezone.now().date()):
        """Checks and settles a cash incentive and return the remittance object. returns false if already settled"""
        if not self.cash_incentive_is_settled():
            self.date_cash_incentive_settlement = timezone.localtime().date()
            return self
        else:
            return False

    def temp_settle_cash_incentive_from_ci_table(self):
        if self.cash_incentive_is_settled()==True and self.cashincentive_set.count()==1:
            c = self.cashincentive_set.first()
            if c.is_settled()==False:
                try:
                    c= c.settle_cash_incentive(date_settle = self.date_cash_incentive_settlement)
                    c.save()
                    return True
                except Exception as e:
                    return e
            else:
                return "Already settled"
        else:
            return "Either cash incentive not settled or multiple cash incentives "+self.reference


    def calculate_cash_incentive(self):
        return self.amount*Decimal(0.025)

    def get_ci_trn_type(self):
        #returns cash incentive transaction type for RIT
        if self.is_thirdparty_remittance():
            return "SUBAGENT_CASHPICKUP"
        elif self.exchange.name=='SWIFT':
            return "OWN BANK ACC CREDIT"
        return None

    """def get_exchange_rate(self, type = 'TTC'):
        if Rate.objects.get(currency=self.currency, rate_type=type, date = self.date_create.date).exists():
            rate = Rate.objects.get(currency=self.currency, rate_type=type, date = self.date_create.date)
            return rate
        else:
            return "DNE"""

    def get_fc_amount(self):
        ## FC value for total remittance regardless the encashment 
        if self.currency.short == 'BDT':
            currency = Currency.objects.get(short='USD')
            if currency.get_exchange_rate(date=self.date_create.date(), type = 'TTC') != 'DNE':
                rate = currency.get_exchange_rate(date=self.date_create.date(), type = 'TTC').rate
                return self.amount/rate
            else:
                return "No Rate"
        else:
            return self.amount

    def get_total_paid_cash_incentive_sum(self):
        ###Returns the sum of all paid cash incentives
        q = self.get_paid_cash_incentives()
        total = 0
        for e in q:
            total = total + e.cash_incentive_amount
        return total

    def change_receiver(self, new_receiver):
        self.receiver = new_receiver
        self.save()
        return self

    def is_thirdparty_remittance(self):
        # returns true if the remittance is from third party exchange house
        return self.exchange.name != 'SWIFT' and self.exchange.name != 'CASH DEPOSIT'
    
    def get_schedule_code(self):
        if self.is_thirdparty_remittance():
            return "24"
        if self.exchange.name == 'SWIFT':
            return "23"
        if self.exchange.name == 'CASH DEPOSIT':
            return "25"
        
    
    

class RemittanceUpdateHistory(models.Model):
    remittance=models.ForeignKey(Remmit, on_delete=models.CASCADE, verbose_name= "Remittance Entry")
    datecreate = models.DateTimeField("Date of Editing", auto_now_add=True)
    createdby = models.ForeignKey(User, on_delete=models.PROTECT)
    ip = models.GenericIPAddressField("User IP Address")

    def __str__(self):
        return self.remittance.reference+" by "+self.createdby.username+" on "+str(self.datecreate)

    
class Encashment(models.Model):
    remittance = models.ForeignKey(Remmit, on_delete=models.CASCADE,)
    amount = models.DecimalField("Amount of Encashment in FC",max_digits=20,decimal_places=2, validators=[validate_neg], help_text="Something ")
    rate = models.DecimalField("Rate of Encashment to BDT",max_digits=8, decimal_places=4, validators=[validate_neg], help_text="Something ")
    PAYMENT= 'P'
    NONPAYMENT = 'U'
    NOTAPPLICABLE = 'NA'
    ENTRYCAT_CHOICES = (
        (PAYMENT,'Pay Now'),
        (NONPAYMENT, 'Pay Later'),
        (NOTAPPLICABLE, 'Not Applicable'),
        )
    cashin_category = models.CharField("Cash Incentive Payment Status", choices=ENTRYCAT_CHOICES, max_length=2, )
    reason = models.CharField('Reason for not paying cash incentive', max_length=100, null=True, blank=True)
    account = models.ForeignKey(Account,verbose_name='Destination Account', on_delete=models.PROTECT, null=True, blank = True)
    createdby = models.ForeignKey(User, on_delete=models.PROTECT)
    date_create = models.DateTimeField("Date of posting", auto_now_add=True)

    def __str__(self):
        return self.remittance.reference+" by "+self.createdby.username+" on "+str(self.date_create)

    def clean(self):
        if self.cashin_category=='U' and (not self.reason):
            raise ValidationError({'reason': _('Reason cannot be left blank if cash incentive is unpaid')})
        #if self.remittance.get_encashment_room()<self.amount:
            #raise ValidationError({'amount': _('Encashment limit exceeded')})
    
    def calculate_cash_incentive(self):
        return self.amount*self.rate*Decimal(0.025)

    def check_cash_incnetive_payment_status(self):
        #Returns true if cash incentive is paid
        if self.cashincentive.entry_category == 'P' and self.cashin_category=='P':
            return "P"
        elif self.cashincentive.entry_category == 'NA' or self.cashin_category=='NA':
            return "NA"
        else:
            return "U"

    def pay_unpaid_cash_incentive(self):
        #q = CashIncentive.objects.filter(encashment=self, entry_category='P').exists()
        if self.check_cash_incnetive_payment_status() == "U":
            self.cashincentive.cash_incentive_amount= self.calculate_cash_incentive()
            self.cashincentive.date_cash_incentive_paid=timezone.now()
            self.cashincentive.entry_category='P'
            self.cashin_category='P'
            self.save()
            self.cashincentive.save()
            return self
        else:
            return False

    def encashment_amount_in_bdt(self):
        if self.remittance.currency.short != 'BDT':
            return self.amount*self.rate
        else:
            return self.amount



class CashIncentive(models.Model):
    remittance = models.ForeignKey(Remmit, on_delete=models.CASCADE,)
    encashment = models.OneToOneField(Encashment, on_delete=models.CASCADE, null=True, blank=True)
    cash_incentive_amount = models.DecimalField("Amount of Cash Incentive",max_digits=20,decimal_places=2, validators=[validate_neg])
    date_cash_incentive_paid = models.DateTimeField("Date of Cash Incentive payment", null=True, blank= True)
    date_cash_incentive_settlement = models.DateField("Date of Cash Incentive Settlement", null=True, blank= True)
    unpaid_cash_incentive_reason = models.CharField("Reason for not paying cash incentive", max_length=50, null=True, blank=True, help_text="This field is mandatory if you mark cash incentive as unpaid")
    PAYMENT= 'P'
    NONPAYMENT = 'U'
    NOTAPPLICABLE = 'NA'
    ENTRYCAT_CHOICES = (
        (PAYMENT,'Pay Now'),
        (NONPAYMENT, 'Pay Later'),
        (NOTAPPLICABLE, 'Not Applicable'),
        )
    entry_category = models.CharField("Cash Incentive Payment Status", choices=ENTRYCAT_CHOICES, max_length=2, )
    partial_payment_status = models.BooleanField("Partial Cash Incentive Payment?", default=False)

    def __str__(self):
        return self.remittance.reference +" "+ self.entry_category + " Encashment ID: "+ (str(self.encashment.id) if self.encashment else " No Encashment")

    def get_fc_amount(self):
        """Get fc value of the remittance for which the cash incentive paid.
        In case of complete encashment gets total FC Value. In case of partial
        encashment gets only the FC value for encashed amount"""
        if self.remittance.is_thirdparty_remittance():
            return self.remittance.get_fc_amount()
        else:
            if self.encashment:
                return self.encashment.amount
            else:
                return None

    def get_bdt_amount(self):
        """Get bdt value of the remittance for which the cash incentive paid.
        In case of complete encashment gets total bdt Value. In case of partial
        encashment gets only the bdt value for encashed amount"""
        if self.remittance.is_thirdparty_remittance() and self.remittance.currency.short=='BDT':
            return self.remittance.amount
        else:
            if self.encashment and self.remittance.currency.short != 'BDT':
                return self.encashment.encashment_amount_in_bdt()
            else:
                return None

    def get_exchange_rate(self):
        """ Return TT Clean rate of the date create of Remittance
            Return TT Clean of encashment date for partial encashment"""
        if self.remittance.is_thirdparty_remittance():
            if self.remittance.currency.short=='BDT':
                currency = Currency.objects.get(short='USD')
                date = self.remittance.date_create.date()
        else:
            if self.encashment:
                currency = self.remittance.currency
                date = self.encashment.date_create.date()
            else:
                return "Encashment entry not found"
        return currency.get_exchange_rate(date=date).rate if currency.get_exchange_rate(date=date) != 'DNE' else 'Rate not Found'
    
    def get_usd_amount(self):
        """ Return USD value of the remittance of CI
            In case of partial encashment, returns USD 
            value of only encashed part """
        if self.remittance.currency.short == 'USD':
            return self.remittance.amount if self.remittance.is_thirdparty_remittance() else self.encashment.amount
        else:
            date = None
            if self.remittance.is_thirdparty_remittance():
                date = self.remittance.date_create.date()
            else:
                if self.encashment:
                    date = self.encashment.date_create.date()
            amount_bdt = self.get_bdt_amount()
            currency = Currency.objects.get(short='USD')
            usd_rate = currency.get_exchange_rate(date=date)
            return amount_bdt/usd_rate.rate if usd_rate != 'DNE' else 'Rate not Found'

    def get_entry_category_display(self):
        if self.entry_category=='P':
            return "Paid"
        if self.entry_category=='U':
            return "Unpaid"
        if self.entry_category=='NA':
            return "Not Applicable"

    def check_if_paid(self):
        if self.entry_category=='P':
            return True
        else:
            return False

    def is_settled(self):
        """Checks whether the payment cash incentive is settled.
            Returns True if settled else False"""
        if self.entry_category=='P' and self.date_cash_incentive_paid and self.date_cash_incentive_settlement:
            return True
        else:
            return False


    def settle_cash_incentive(self, date_settle= timezone.now().date()):
        """Checks and settles a cash incentive and return the remittance object. returns false if already settled"""
        if not self.is_settled():
            self.date_cash_incentive_settlement = timezone.localtime().date()
            return self
        else:
            return False


    def create_entry_from_remittance(self, remitt):
        if remitt.check_unpaid_cash_incentive():
            try:
                self.remittance=remitt
                self.cash_incentive_amount=0
                self.date_cash_incentive_paid=None
                self.date_cash_incentive_settlement=None
                self.unpaid_cash_incentive_reason=remitt.unpaid_cash_incentive_reason
                self.entry_category = 'U'
                #self.partial_payment_status = True
                self.save()
                return True
            except Exception as e:
                print(e , remitt)

        elif not remitt.date_create.date()>datetime.date(2019,6,30):
            try:
                self.remittance=remitt
                self.cash_incentive_amount=0
                self.date_cash_incentive_paid=None
                self.date_cash_incentive_settlement=None
                self.unpaid_cash_incentive_reason=remitt.unpaid_cash_incentive_reason
                self.entry_category = 'NA'
                self.save()
                return True
            except Exception as e:
                print(e , remitt)
        else:
            try:
                self.remittance=remitt
                self.cash_incentive_amount= remitt.cash_incentive_amount
                self.date_cash_incentive_paid= remitt.date_cash_incentive_paid
                self.date_cash_incentive_settlement= remitt.date_cash_incentive_settlement
                self.unpaid_cash_incentive_reason=remitt.unpaid_cash_incentive_reason + "-SP" if remitt.unpaid_cash_incentive_reason else None
                self.entry_category = 'P'
                self.save()
                return True
            except Exception as e:
                print(e, remitt)
    



class Requestpay(models.Model):
    remittance = models.ForeignKey(Remmit, on_delete=models.CASCADE)
    datecreate = models.DateTimeField("Date of request", auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    REVIEW= 'RV'
    REJECTED = 'RJ'
    PAID = 'PD'
    STATUS_CHOICES = (
        (REVIEW,'Request to be Processed'),
        (REJECTED, 'Request Rejected'),
        (PAID, 'Amount Payable to Customer'),
        )
    status=models.CharField("Request Status",max_length=2, choices=STATUS_CHOICES, default=REVIEW)
    comment = models.TextField("Reason for rejection or any other remarks",null=True)
    resubmit_flag = models.BooleanField("Resubmit Yes/No",default=False)
    ip = models.GenericIPAddressField("User IP Address")
    #payment = models.ForeignKey('Payment',  null=True, on_delete=models.SET_NULL)"""

    def __str__(self):
        return self.remittance.reference+" on "+self.remittance.branch.name
    
    def is_in_review(self):
        return True if self.status=='RV' else False

    def is_rejected(self):
        return True if self.status=='RJ' else False
    
    def is_accepted_for_settlement(self):
        return True if self.status=='PD' else False

    def mark_rejected(self):
        if not (self.is_rejected() or self.is_accepted_for_settlement()):
            self.status = 'RJ'
            return self

    def accept_for_settlement(self):
        if self.is_in_review():
            self.status = 'PD'
            return self


class Payment(models.Model):
    requestpay = models.OneToOneField(Requestpay, on_delete=models.PROTECT)
    dateresolved = models.DateTimeField("Date of payment/rejection", auto_now_add=True)
    UNSETTLED= 'U'
    SETTLED = 'S'
    STATUS_CHOICES = (
        (UNSETTLED,'Payment yet to be settled'),
        (SETTLED, 'Payment settled'),
        )
    status=models.CharField("Status",max_length=1, choices=STATUS_CHOICES, default=UNSETTLED)
    paid_by = models.ForeignKey(User, on_delete=models.PROTECT)
    settled_by = models.ForeignKey(User, on_delete=models.PROTECT, null=True, related_name='settlements', blank=True)
    date_settle = models.DateTimeField("Date of settlement", null=True, validators=[validate_post_date], blank=True)
    agent_screenshot = models.ImageField("Agent Copy",upload_to = 'images/%Y/%m/%d/', default = 'images/None/no-img.jpg')
    western_trm_screenshot = models.ImageField("Pre Transaction Receipt",upload_to = 'western_trm/%Y/%m/%d/', default = 'images/None/no-img.jpg')
    customer_screenshot = models.ImageField("Customer Copy",upload_to = 'western_trm/%Y/%m/%d/', default = 'images/None/no-img.jpg')
    ip = models.GenericIPAddressField("User IP Address")

    def __str__(self):
        return self.requestpay.remittance.reference+" on "+self.requestpay.remittance.branch.name

    def is_settled(self):
        """Checks whether the payment remittance is settled.
            Returns True if settled else False"""
        if self.status=='S' and self.settled_by and self.date_settle:
            return True
        else:
            return False

    def settle_remittance(self,user):
        """Checks and settles a Payment and return the payment object. returns false if already settled"""
        if not self.is_settled() and self.requestpay.remittance.is_thirdparty_remittance():
            self.status = 'S'
            self.date_settle = timezone.now()
            self.settled_by=user
            return self
        else:
            return False

    def unsettle_remittance(self):
        """Checks and UNsettles a Payment and return the payment object. returns false if not settled"""
        if self.is_settled():
            self.status = 'U'
            self.date_settle = None
            self.settled_by=None
            return self
        else:
            return False

class Claim(models.Model):
    date_claim = models.DateTimeField("Date of Claim", auto_now_add=True, )
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    statement_check = models.BooleanField("Benificary Account Statement checked ?", help_text="Beneficiary account statement must be checked before submission of cash incentive claim")
    account_no=models.CharField("Benificary Account Number",max_length=15,validators=[nrbc_acc,])
    account_title=models.CharField("Benificary Account Title",max_length=100, validators=[name,])
    date_account_credit = models.DateField("Date of Account Credit" )
    BEFTN= 'B'
    RTGS = 'R'
    CHANNEL_CHOICES = (
        (BEFTN,'BEFTN'),
        (RTGS, 'RTGS'),
        )
    channel=models.CharField("Channel of A/C Credit",max_length=1, choices=CHANNEL_CHOICES)
    collecting_bank=models.ForeignKey(Bank, on_delete=models.CASCADE, verbose_name='Collecting Bank', limit_choices_to= Q(type='PRIVATE COMMERCIAL BANK') | Q(type='STATE-OWNED COMMERCIAL BANK') | Q(type='FOREIGN COMMERCIAL BANKS'))
    document_check = models.BooleanField("Remitters Document Checked ?", help_text="Remitter's documents must be checked before submission of cash incentive claim")
    sender_name=models.CharField("Remitter's Name", max_length=100, validators=[name,])
    passport_no = models.CharField("Passport Number", max_length=17)
    passport_issuing_country=models.ForeignKey(Country, on_delete=models.CASCADE, verbose_name="Passport Issuing Country")
    visa_check = models.BooleanField(" \"NO Visa Required to Travel Bangladesh\" Document Obtained?" , help_text="Applicable & Mandatory to obtain for Foreign Passport Holders only", null=True)
    passport_expire = models.DateField("Expiry Date of Remitter's Passport", validators=[validate_expire_date,])
    doc_type=models.CharField("Remitter's Other Document Type", max_length=50)
    doc_no = models.CharField("Remitter's Other Document Number", max_length=50, validators=[alpha_num,])
    doc_issuing_country=models.ForeignKey(Country, related_name='doc_issuing_country', on_delete=models.CASCADE, verbose_name="Other Document Issuing Country")
    doc_expire = models.DateField("Expiry Date of Remitter's Other Document", validators=[validate_expire_date,])
    letter_check = models.BooleanField("Beneficiary's Letter of Incentive Claim Received?", help_text="Beneficiary's Letter of Incentive Claim must be obtained before submission of claim")
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    remittance_amount = models.DecimalField("Amount of Remittance in BDT",max_digits=20,decimal_places=2, validators=[validate_neg], help_text="Required documents must be collected and retained for paying inentive against Remittances valuing more than BDT 5,00,000.00")
    date_forward = models.DateTimeField("Date of Claim forwarded to collecting Bank", null=True, blank=True)
    date_resolved = models.DateTimeField("Date of Claim realized from collecting Bank", null=True, blank=True)

    def forward_check(self):
        """Checks if the claim is
        forwardable"""
        if self.date_forward or self.date_resolved:
            return False
        else:
            return True

    def forward_claim(self):
        if self.forward_check():
            self.date_forward=timezone.now()
            self.save()
            return True
        else:
            return False

    def resolve_check(self):
        """Checks if the claim is
        resolved"""
        if (not self.date_forward) or self.date_resolved:
            return False
        else:
            return True

    def mark_resolved(self):
        if self.resolve_check():
            self.date_resolved=timezone.now()
            self.save()
            return True
        else:
            return False
