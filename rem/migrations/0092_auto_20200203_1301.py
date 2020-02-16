# Generated by Django 2.2.5 on 2020-02-03 07:01

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rem', '0091_auto_20200130_1546'),
    ]

    operations = [
        migrations.AlterField(
            model_name='claim',
            name='account_title',
            field=models.CharField(max_length=100, validators=[django.core.validators.RegexValidator('^[a-zA-Z .-]*$', 'Only alphabets are allowed.')], verbose_name='Benificary Account Title'),
        ),
        migrations.AlterField(
            model_name='claim',
            name='doc_no',
            field=models.CharField(max_length=50, validators=[django.core.validators.RegexValidator('^[0-9a-zA-Z]*$', 'Only Alphabet and numeric characters are allowed.')], verbose_name="Remitter's Other Document Number"),
        ),
        migrations.AlterField(
            model_name='claim',
            name='passport_no',
            field=models.CharField(max_length=17, verbose_name='Passport Number'),
        ),
        migrations.AlterField(
            model_name='claim',
            name='sender_name',
            field=models.CharField(max_length=100, validators=[django.core.validators.RegexValidator('^[a-zA-Z .-]*$', 'Only alphabets are allowed.')], verbose_name="Remitter's Name"),
        ),
        migrations.AlterField(
            model_name='remittanceupdatehistory',
            name='remittance',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rem.Remmit', verbose_name='Remittance Entry'),
        ),
        migrations.AlterField(
            model_name='remmit',
            name='cash_incentive_status',
            field=models.CharField(choices=[('P', 'Paid'), ('U', 'Unpaid')], max_length=1, verbose_name='Cash Incentive Status'),
        ),
        migrations.AlterField(
            model_name='requestpay',
            name='remittance',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rem.Remmit'),
        ),
    ]