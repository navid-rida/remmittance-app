# Generated by Django 2.2.16 on 2022-03-02 11:53

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import rem.validators


class Migration(migrations.Migration):

    dependencies = [
        ('rem', '0130_auto_20220105_1936'),
    ]

    operations = [
        migrations.AddField(
            model_name='remmit',
            name='ordering_bank_name',
            field=models.CharField(max_length=60, null=True, verbose_name='F50K: Name of Ordering Institution'),
        ),
        migrations.AddField(
            model_name='remmit',
            name='ordering_bank_swift',
            field=models.CharField(max_length=11, null=True, verbose_name='F50K: SWIFT BIC of Ordering Institution'),
        ),
        migrations.AlterField(
            model_name='cashincentive',
            name='remittance',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rem.Remmit'),
        ),
        migrations.AlterField(
            model_name='encashment',
            name='cashin_category',
            field=models.CharField(choices=[('P', 'Pay Now'), ('U', 'Pay Later'), ('NA', 'Not Applicable')], max_length=2, verbose_name='Cash Incentive Payment Status'),
        ),
        migrations.AlterField(
            model_name='encashment',
            name='remittance',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rem.Remmit'),
        ),
        migrations.AlterField(
            model_name='remittanceupdatehistory',
            name='remittance',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rem.Remmit', verbose_name='Remittance Entry'),
        ),
        migrations.AlterField(
            model_name='remmit',
            name='amount',
            field=models.DecimalField(decimal_places=2, help_text='Required documents must be collected and retained for paying inentive against Remittances valuing more than BDT 5,00,000.00 or USD 5,000.00 or equivalent FC', max_digits=20, validators=[rem.validators.validate_neg], verbose_name='Amount of Remittance'),
        ),
        migrations.AlterField(
            model_name='remmit',
            name='mariner_status',
            field=models.BooleanField(choices=[(True, 'Yes'), (False, 'No')], help_text='Mark yes if the remittance remitted by Foreign Shipping Lines/ Airlines/ UN or UN Bodies/ Foreign Missions', verbose_name='Mariner/ Cabin Crew Remittance?'),
        ),
        migrations.AlterField(
            model_name='remmit',
            name='reference',
            field=models.CharField(help_text="Referene No./PIN/MTCN/ For SWIFT - Sender's reference: F20A", max_length=16, unique=True, verbose_name='Referene No./PIN/MTCN'),
        ),
        migrations.AlterField(
            model_name='remmit',
            name='relationship',
            field=models.CharField(choices=[('FM', 'Family'), ('FR', 'Friend'), ('BA', 'Business Associate'), ('CL', 'Client'), ('EM', 'Employee'), ('ER', 'Employer'), ('AC', 'Acquaintance')], max_length=50, null=True, verbose_name="Benificiary's relationship to Sender"),
        ),
        migrations.AlterField(
            model_name='remmit',
            name='sender_bank',
            field=models.CharField(blank=True, help_text='Ordering Institution: F52A for remittance through SWIFT', max_length=100, null=True, verbose_name="Sender's Bank/ Ordering Institution"),
        ),
        migrations.AlterField(
            model_name='remmit',
            name='sender_bank_swift',
            field=models.CharField(blank=True, help_text="Ordering Institution's SWIFT BIC: F52A for remittance through SWIFT", max_length=11, null=True, validators=[django.core.validators.RegexValidator('^[0-9A-Z]{11}$', 'Please provide a valid SWIFT BIC')], verbose_name="Sender's Bank's/ Ordering Institution's SWIFT BIC"),
        ),
        migrations.AlterField(
            model_name='requestpay',
            name='remittance',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rem.Remmit'),
        ),
    ]