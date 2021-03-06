# Generated by Django 2.0.7 on 2018-07-23 10:02

import datetime
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import rem.validators


class Migration(migrations.Migration):

    dependencies = [
        ('rem', '0009_auto_20180723_1020'),
    ]

    operations = [
        migrations.AddField(
            model_name='remmit',
            name='reference',
            field=models.CharField(default=11111111, max_length=16, validators=[django.core.validators.RegexValidator('^[0-9]*$', 'Only numeric characters are allowed.')], verbose_name='Referene No.'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='remmit',
            name='date',
            field=models.DateField(default=datetime.date(2018, 7, 23), validators=[rem.validators.validate_post_date], verbose_name='Remmittance Distribution Date'),
        ),
        migrations.AlterField(
            model_name='remmit',
            name='exchange',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rem.ExchangeHouse', verbose_name='Exchange House'),
        ),
        migrations.AlterField(
            model_name='remmit',
            name='rem_country',
            field=models.CharField(max_length=20, verbose_name='Name of Remmitting Country'),
        ),
    ]
