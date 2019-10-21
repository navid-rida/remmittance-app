from django.db import models
from decimal import Decimal
#from datetime import date
from django.core.exceptions import ValidationError
from .validators import validate_neg, validate_post_date, validate_mobile, numeric, name, alpha, alpha_num, western_union
from django.core.validators import RegexValidator
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
import pandas as pd
from rem.DataModels import filter_remittance
########################## aggregate functions ###############################
from django.db.models import Sum
################# import for validation errrors ##############################
from django.utils.translation import gettext_lazy as _

####################### Rules ################################
import rem.rule_set
import rules

######################### Custom Managers ###############################
# Create your models here.

class Branch(models.Model):
    name = models.CharField("Name of The branch", max_length=20,default='Principal')
    code = models.CharField("Branch Code", validators=[numeric], max_length=4,default='0101')
    ad_code = models.CharField("AD Code", validators=[numeric], max_length=4, null=True)
    division = models.CharField("Division", validators=[alpha], max_length=20)
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
    name = models.CharField("Name of the Booth", max_length=20)
    code = models.CharField("Booth Code", validators=[numeric], max_length=4)
    address = models.TextField("Address of the Booth")
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


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, verbose_name='Branch of the Employee')
    booth = models.ForeignKey(Booth, on_delete=models.CASCADE, verbose_name='Booth of the Employee', null=True, blank=True)
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

    def get_related_remittance(self, start_date=None, end_date= None, branch= None, booth= None, exchange_house=None):
        query_set = Remmit.objects.all()
        if self.user.has_perm('rem.view_all_remitt'):
            rem = filter_remittance(query_set = query_set, start_date=start_date, end_date= end_date, branch= branch, booth= booth, exchange_house=exchange_house)
        elif self.user.has_perm('rem.view_branch_remitt'):
            rem = filter_remittance(query_set = query_set, start_date=start_date, end_date= end_date, branch= self.branch, booth= booth, exchange_house=exchange_house)
        elif self.user.has_perm('rem.view_booth_remitt'):
            rem = filter_remittance(query_set = query_set, start_date=start_date, end_date= end_date, booth= self.booth, exchange_house=exchange_house)
        else:
            if self.booth:
                query_set = self.user.remmit_set.filter(booth=self.booth)
                rem = filter_remittance(query_set = query_set, start_date=start_date, end_date= end_date, exchange_house=exchange_house)
            else:
                query_set = self.user.remmit_set.filter(branch=self.branch)
                rem = filter_remittance(query_set = query_set, start_date=start_date, end_date= end_date, booth= booth, exchange_house=exchange_house)
        return rem

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
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, default=0)


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

class ReceiverUpdateHistory(models.Model):
    receiver=models.ForeignKey(Receiver, on_delete=models.CASCADE, verbose_name= "Receiver")
    datecreate = models.DateTimeField("Date of Editing", auto_now_add=True)
    createdby = models.ForeignKey(User, on_delete=models.PROTECT)
    ip = models.GenericIPAddressField("User IP Address")


class ExchangeHouse(models.Model):
    name = models.CharField("Name of Exchange House", max_length=30)
    gl_no = models.CharField("GL Head of Exchange House", max_length=15,  validators=[numeric])
    cash_incentive_gl_no = models.CharField("GL Head of Cash Incentive distribution", max_length=15,  validators=[numeric])
    ac_no = models.CharField("Account no. of Exchange House", max_length=11,  validators=[numeric])

    def __str__(self):
        return self.name

class Remmit(models.Model):
    exchange = models.ForeignKey(ExchangeHouse,on_delete=models.CASCADE, verbose_name='Channel of Remittance')
    rem_country = models.ForeignKey(Country,on_delete=models.CASCADE, verbose_name='Remitting Country')
    sender = models.CharField("Name of Remitter", validators=[name], max_length=50)
    relationship = models.CharField("Relationship to Sender",max_length=50, null=True)
    purpose = models.CharField("Purpose of Transaction",max_length=50, null=True)
    PAID= 'P'
    HELD = 'H'
    UNPAID = 'U'
    CASHINC_CHOICES = (
        (PAID,'Paid'),
        #(HELD, 'Held'),
        (UNPAID, 'Unpaid'),
        )
    cash_incentive_status = models.CharField("Cash Incentive Status", choices=CASHINC_CHOICES, max_length=1, help_text="Please select 'Held' if required documents not collected and incentive not paid")
    unpaid_cash_incentive_reason = models.CharField("Reason for not paying cash incentive", max_length=50, null=True, blank=True, help_text="This field is mandatory if you mark cash incentive as unpaid")
    receiver = models.ForeignKey(Receiver, on_delete=models.PROTECT, verbose_name="Receiver")
    amount = models.DecimalField("Amount of Payment",max_digits=20,decimal_places=2, validators=[validate_neg], help_text="Required documents must be collected and retained for paying inentive against Remittances valuing more than USD 1500.00 or equivalent")
    cash_incentive_amount = models.DecimalField("Amount of Cash Incentive",max_digits=20,decimal_places=2, validators=[validate_neg])
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    booth = models.ForeignKey(Booth, on_delete=models.CASCADE, null=True, blank=True)
    date_sending = models.DateField("Date of Sending Remittance from Abroad")
    date_cash_incentive_settlement = models.DateField("Date of Cash Incentive Settlement", null=True, blank= True)
    date_create = models.DateTimeField("Date of posting", auto_now_add=True)
    date_edited = models.DateTimeField("Date of last modified", auto_now=True)
    reference = models.CharField("Referene No./PIN/MTCN", max_length=16, unique=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    edited_by = models.ForeignKey(User, on_delete=models.PROTECT, null=True, related_name='editors')
    REVIEW= 'RV'
    REJECTED = 'RJ'
    PAID = 'PD'
    """STATUS_CHOICES = (
        (REVIEW,'Request to be Processed'),
        (REJECTED, 'Request Rejected'),
        (PAID, 'Amount Payable to Customer'),
        )
    status=models.CharField("Request Status",max_length=2, choices=STATUS_CHOICES, default=REVIEW)"""
    def __str__(self):
        return self.reference+" on "+self.branch.name

    def get_completed_payment(self):
        r = self.requestpay_set.order_by('datecreate',).last()
        if r.payment:
            return r.payment
        else:
            return False

class RemittanceUpdateHistory(models.Model):
    remittance=models.ForeignKey(Remmit, on_delete=models.CASCADE, verbose_name= "Remittance Entry")
    datecreate = models.DateTimeField("Date of Editing", auto_now_add=True)
    createdby = models.ForeignKey(User, on_delete=models.PROTECT)
    ip = models.GenericIPAddressField("User IP Address")


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
