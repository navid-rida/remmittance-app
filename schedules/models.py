from django.db import models
from rem.validators import validate_neg, validate_post_date, validate_mobile, numeric, name, alpha, alpha_num, western_union, nrbc_acc

# Create your models here.

class Currency(models.Model):
    name = models.CharField("Name of Currenct", max_length=50)
    ccy_id = models.CharField("CCY ID", max_length=4,  validators=[numeric])
    cur_code = models.CharField("Currency Code", max_length=3,  validators=[numeric])
    short = models.CharField("Short Code", max_length=3,  validators=[alpha])

    def __str__(self):
        return self.name

class District(models.Model):
    name = models.CharField("Name of District", max_length=40)
    code= models.CharField("District Code", max_length=3,  validators=[numeric])

    def __str__(self):
        return self.name

class Bank(models.Model):
    name = models.CharField("Name of Bank", max_length=60)
    fi_id= models.CharField("FI ID", max_length=4,  validators=[numeric])
    type = models.CharField("Type of Institution", max_length=60)

    def __str__(self):
        return self.name

class Rate(models.Model):
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    BC_SELLING = 'BCS'
    TT_CLEAN = 'TTC'
    RATE_TYPE_CHOICES = (
        (BC_SELLING,'BC SELLING'),
        (TT_CLEAN, 'TT CLEAN')
        )
    rate_type = models.CharField("Type of Exchange Rate", choices=RATE_TYPE_CHOICES, max_length=3)
    date = models.DateField("Date of Entry")
    rate = models.DecimalField("Exchange Rate in BDT", max_digits=7,decimal_places=2, validators=[validate_neg],)