from django.db import models
from rem.validators import validate_neg, validate_post_date, validate_mobile, numeric, name, alpha, alpha_num, western_union, nrbc_acc

# Create your models here.

class Currency(models.Model):
    name = models.CharField("Name of Currenct", max_length=50)
    ccy_id = models.CharField("CCY ID", max_length=4,  validators=[numeric])
    cur_code = models.CharField("Currency Code", max_length=3,  validators=[numeric])

    def __str__(self):
        return self.name

class District(models.Model):
    name = models.CharField("Name of District", max_length=40)
    code= models.CharField("District Code", max_length=3,  validators=[numeric])

    def __str__(self):
        return self.name
