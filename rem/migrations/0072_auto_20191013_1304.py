# Generated by Django 2.2.5 on 2019-10-13 07:04

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import rem.validators


class Migration(migrations.Migration):

    dependencies = [
        ('rem', '0071_auto_20191010_1832'),
    ]

    operations = [
        migrations.AddField(
            model_name='exchangehouse',
            name='cash_incentive_gl_no',
            field=models.CharField(default=125654125658125, max_length=15, validators=[django.core.validators.RegexValidator('^[0-9]*$', 'Only numeric characters are allowed.')], verbose_name='GL Head of Cash Incentive distribution'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='remittanceupdatehistory',
            name='remittance',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rem.Remmit', verbose_name='Remittance Entry'),
        ),
        migrations.AlterField(
            model_name='remmit',
            name='amount',
            field=models.DecimalField(decimal_places=2, help_text='Required documents must be collected and retained for paying inentive against Remittances valuing more than USD 1500.00 or equivalent', max_digits=20, validators=[rem.validators.validate_neg], verbose_name='Amount of Payment'),
        ),
        migrations.AlterField(
            model_name='remmit',
            name='cash_incentive_status',
            field=models.CharField(choices=[('P', 'Paid'), ('H', 'Held'), ('U', 'Unpaid')], help_text="Please select 'Held' if required documents not collected and incentive not paid", max_length=1, verbose_name='Cash Incentive Status'),
        ),
        migrations.AlterField(
            model_name='requestpay',
            name='remittance',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rem.Remmit'),
        ),
    ]