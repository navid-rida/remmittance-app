# Generated by Django 2.0.7 on 2019-05-22 07:53

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rem', '0063_auto_20190509_1358'),
    ]

    operations = [
        migrations.AlterField(
            model_name='branch',
            name='code',
            field=models.CharField(default='0101', max_length=4, validators=[django.core.validators.RegexValidator('^[0-9]*$', 'Only numeric characters are allowed.')], verbose_name='Branch Code'),
        ),
        migrations.AlterField(
            model_name='receiver',
            name='name',
            field=models.CharField(max_length=100, validators=[django.core.validators.RegexValidator('^[a-zA-Z .-]*$', 'Only alphabets are allowed.')], verbose_name='Name of Receiver'),
        ),
        migrations.AlterField(
            model_name='remittanceupdatehistory',
            name='remittance',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rem.Remmit', verbose_name='Remittance Entry'),
        ),
        migrations.AlterField(
            model_name='remmit',
            name='sender',
            field=models.CharField(max_length=50, validators=[django.core.validators.RegexValidator('^[a-zA-Z .-]*$', 'Only alphabets are allowed.')], verbose_name='Name of Remitter'),
        ),
        migrations.AlterField(
            model_name='requestpay',
            name='remittance',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rem.Remmit'),
        ),
    ]
