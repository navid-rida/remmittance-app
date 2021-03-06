# Generated by Django 2.0.7 on 2018-07-18 08:53

import datetime
from decimal import Decimal
import django.core.validators
from django.db import migrations, models
import rem.validators


class Migration(migrations.Migration):

    dependencies = [
        ('rem', '0003_remmit_branch'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExchangeHouse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20, verbose_name='Name of Exchange House')),
                ('gl_no', models.CharField(max_length=15, validators=[django.core.validators.RegexValidator('^[0-9]*$', 'Only numeric characters are allowed.')], verbose_name='GL Head of Exchange House')),
                ('ac_no', models.CharField(max_length=11, validators=[django.core.validators.RegexValidator('^[0-9]*$', 'Only numeric characters are allowed.')], verbose_name='Account no. of Exchange House')),
            ],
        ),
        migrations.AlterField(
            model_name='remmit',
            name='amount',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=20, validators=[rem.validators.validate_even]),
        ),
        migrations.AlterField(
            model_name='remmit',
            name='date',
            field=models.DateField(default=datetime.date(2018, 7, 18), verbose_name='Remmittance Distribution Date'),
        ),
    ]
