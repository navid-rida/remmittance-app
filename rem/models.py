from django.db import models
from decimal import Decimal
from datetime import date
from .validators import validate_neg, validate_post_date
from django.core.validators import RegexValidator
from django.contrib.auth.models import User
from django.utils import timezone
# Create your models here.
numeric = RegexValidator(r'^[0-9]*$', 'Only numeric characters are allowed.')
alpha_num = RegexValidator(r'^[0-9a-zA-Z]*$', 'Only Alphabet and numeric characters are allowed.')


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

class ExchangeHouse(models.Model):
    name = models.CharField("Name of Exchange House", max_length=30)
    gl_no = models.CharField("GL Head of Exchange House", max_length=15,  validators=[numeric])
    ac_no = models.CharField("Account no. of Exchange House", max_length=11,  validators=[numeric])

    def __str__(self):
        return self.name

class Remmit(models.Model):
    #branch = models.ForeignKey(Branch, on_delete = models.CASCADE)
    WESTERN = 'WU'
    MONEYGRAM = 'MG'
    RIA = 'RI'
    EXPRESSMONEY = 'EM'
    PLACID = 'EM'
    EXCHANGE_CHOICES = (
        (WESTERN, 'Western Union'),
        (MONEYGRAM, 'MoneyGram'),
        (EXPRESSMONEY, 'Express Money'),
        (RIA, 'Ria'),
        (PLACID,'Placid'),
        )
    exchange = models.ForeignKey(ExchangeHouse,on_delete=models.CASCADE, verbose_name='Exchange House')
    rem_country = models.ForeignKey(Country,on_delete=models.CASCADE, verbose_name='Name of Country')
    sender = models.CharField("Name of Remmitter",max_length=30)
    reciever = models.CharField("Name of Benificiary",max_length=30)
    amount = models.DecimalField(max_digits=20,decimal_places=2, default=Decimal('0.00'), validators=[validate_neg])
    CASH= 'C'
    TRANSFER = 'T'
    MODE_CHOICES = (
        (CASH,'Cash'),
        (TRANSFER, 'Transfer'),
        )
    mode = models.CharField("Mode of Transaction",max_length=1, choices=MODE_CHOICES, default=CASH)
    SETTLED= 'ST'
    NOT_SETTLED = 'NS'
    PENDING = 'PS'
    STATUS_CHOICES = (
        (SETTLED,'Settled'),
        (NOT_SETTLED, 'Not Settled'),
        )
    status = models.CharField("Status",max_length=2, choices=STATUS_CHOICES, default=NOT_SETTLED)
    date = models.DateField("Remmittance Distribution Date", default=timezone.now, validators=[validate_post_date])
    date_settle = models.DateField("Remmittance Settement Date", null=True, validators=[validate_post_date])
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    date_create = models.DateField("Date of posting", auto_now_add=True)
    date_edited = models.DateField("Date of last modified", auto_now=True)
    reference = models.CharField("Referene No.", max_length=16,  validators=[alpha_num])
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def status_verbose(self):
        if self.status == 'ST':
            return "Settled"
        elif self.status == 'PS':
            return "Downloaded for settlement"
        else:
            return "Not Settled"
