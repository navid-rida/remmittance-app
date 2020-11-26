# Generated by Django 2.2.5 on 2020-11-26 06:44

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import rem.validators


class Migration(migrations.Migration):

    dependencies = [
        ('rem', '0099_auto_20200601_1617'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booth',
            name='address',
            field=models.TextField(verbose_name='Address of the Sub-branch'),
        ),
        migrations.AlterField(
            model_name='booth',
            name='code',
            field=models.CharField(max_length=4, unique=True, validators=[django.core.validators.RegexValidator('^[0-9]*$', 'Only numeric characters are allowed.')], verbose_name='Sub-branch Code'),
        ),
        migrations.AlterField(
            model_name='booth',
            name='name',
            field=models.CharField(max_length=20, verbose_name='Name of the Sub-branch'),
        ),
        migrations.AlterField(
            model_name='claim',
            name='account_no',
            field=models.CharField(max_length=15, validators=[django.core.validators.RegexValidator('^01[0-7][0-9][2-3][0-9]{10}$', 'Please provide a valid NRBC account number')], verbose_name='Benificary Account Number'),
        ),
        migrations.AlterField(
            model_name='claim',
            name='remittance_amount',
            field=models.DecimalField(decimal_places=2, help_text='Required documents must be collected and retained for paying inentive against Remittances valuing more than BDT 5,00,000.00', max_digits=20, validators=[rem.validators.validate_neg], verbose_name='Amount of Remittance in BDT'),
        ),
        migrations.AlterField(
            model_name='employee',
            name='booth',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='rem.Booth', verbose_name='Sub-branch of the Employee'),
        ),
        migrations.AlterField(
            model_name='exchangehouse',
            name='ac_no',
            field=models.CharField(max_length=15, validators=[django.core.validators.RegexValidator('^[0-9]*$', 'Only numeric characters are allowed.')], verbose_name='Account no. of Exchange House'),
        ),
        migrations.AlterField(
            model_name='receiver',
            name='ac_no',
            field=models.CharField(blank=True, max_length=15, null=True, validators=[django.core.validators.RegexValidator('^01[0-7][0-9][2-3][0-9]{10}$', 'Please provide a valid NRBC account number')], verbose_name='Account Number of the receiver (If any)'),
        ),
        migrations.AlterField(
            model_name='remittanceupdatehistory',
            name='remittance',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rem.Remmit', verbose_name='Remittance Entry'),
        ),
        migrations.AlterField(
            model_name='remmit',
            name='amount',
            field=models.DecimalField(decimal_places=2, help_text='Required documents must be collected and retained for paying inentive against Remittances valuing more than BDT 5,00,000.00', max_digits=20, validators=[rem.validators.validate_neg], verbose_name='Amount of Remittance'),
        ),
        migrations.AlterField(
            model_name='requestpay',
            name='remittance',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rem.Remmit'),
        ),
    ]
