from django.db import models
from decimal import Decimal
#from datetime import date
from .validators import validate_neg, validate_post_date, validate_mobile
from django.core.validators import RegexValidator
from django.contrib.auth.models import User
from django.utils import timezone


# Create your models here.
numeric = RegexValidator(r'^[0-9]*$', 'Only numeric characters are allowed.')
alpha_num = RegexValidator(r'^[0-9a-zA-Z]*$', 'Only Alphabet and numeric characters are allowed.')
western_union = RegexValidator(r'^[0-9]{10}$', 'Western union mtcn can contain only 10 digit numbers')


class Branch(models.Model):
    name = models.CharField("Name of The branch", max_length=20,default='Principal')
    code = models.CharField("Branch Code", max_length=4,default='0101')
    address = models.TextField("Address of the branch")

    def __str__(self):
        return self.name

class Country(models.Model):
    name = models.CharField("Name of The Country", max_length=50)
    code = models.CharField("Country code", max_length=20)

    def __str__(self):
        return self.name


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    branch = models.ForeignKey(Branch,on_delete=models.CASCADE, verbose_name='Branch of the Employee')
    def __str__(self):
        return self.user.get_full_name()

class Receiver(models.Model):
    name = models.CharField("Name of Receiver", max_length=100)
    address = models.TextField("Address of Receiver")
    dob = models.DateField("Date of Birth of Receiver")
    cell = models.CharField("Cell number of Receiver", validators=[validate_mobile], max_length=14, unique=True)
    NID= 'NID'
    PASSPORT = 'PASSPORT'
    BC = 'BC'
    STATUS_CHOICES = (
        (NID,'National ID'),
        (PASSPORT, 'Passport'),
        (BC, 'Birth Regestration Certificate'),
        )
    idtype=models.CharField("Type o Identification",max_length=8, choices=STATUS_CHOICES, default=NID)
    idissue = models.DateField("Issue date of Identification Document", default=timezone.now)
    idexpire = models.DateField("Expiry date of Identification Document", null=True)
    idno = models.CharField("ID Number", max_length=17, unique=True)
    def __str__(self):
        return self.name

class ExchangeHouse(models.Model):
    name = models.CharField("Name of Exchange House", max_length=30)
    gl_no = models.CharField("GL Head of Exchange House", max_length=15,  validators=[numeric])
    ac_no = models.CharField("Account no. of Exchange House", max_length=11,  validators=[numeric])

    def __str__(self):
        return self.name

class Remmit(models.Model):
    exchange = models.ForeignKey(ExchangeHouse,on_delete=models.CASCADE, verbose_name='Channel of Remittance')
    rem_country = models.ForeignKey(Country,on_delete=models.CASCADE, verbose_name='Name of Country')
    sender = models.CharField("Name of Remitter",max_length=50)
    receiver = models.ForeignKey(Receiver, on_delete=models.PROTECT, verbose_name="Receiver")
    amount = models.DecimalField("Amount of Payment",max_digits=20,decimal_places=2, validators=[validate_neg])
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    date_create = models.DateTimeField("Date of posting", auto_now_add=True)
    date_edited = models.DateTimeField("Date of last modified", auto_now=True)
    reference = models.CharField("Referene No./PIN/MTCN", max_length=16, unique=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    edited_by = models.ForeignKey(User, on_delete=models.PROTECT, null=True, related_name='editors')


class Requestpay(models.Model):
    remittance = models.ForeignKey(Remmit, on_delete=models.CASCADE)
    datecreate = models.DateTimeField("Date of request", auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    REVIEW= 'RV'
    REJECTED = 'RJ'
    PAID = 'PD'
    STATUS_CHOICES = (
        (REVIEW,'Request staged for review'),
        (REJECTED, 'Request rejected'),
        (PAID, 'Amount paid to customer'),
        )
    status=models.CharField("Request Status",max_length=2, choices=STATUS_CHOICES, default=REVIEW)
    comment = models.TextField("Reason for rejection or any other remarks",null=True)
    resubmit_flag = models.BooleanField("Resubmit Yes/No",default=False)
    #payment = models.ForeignKey('Payment',  null=True, on_delete=models.SET_NULL)"""

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
    settled_by = models.ForeignKey(User, on_delete=models.PROTECT, null=True, related_name='settlements')
    date_settle = models.DateTimeField("Date of settlement", null=True, validators=[validate_post_date])
    screenshot = models.ImageField(upload_to = 'images/%Y/%m/%d/', default = 'images/None/no-img.jpg')
