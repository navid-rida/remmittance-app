# Generated by Django 2.2.5 on 2019-10-27 08:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rem', '0079_auto_20191023_1518'),
    ]

    operations = [
        migrations.AddField(
            model_name='remmit',
            name='date_cash_incentive_paid',
            field=models.DateField(blank=True, null=True, verbose_name='Date of Cash Incentive payment'),
        ),
        migrations.AlterField(
            model_name='remittanceupdatehistory',
            name='remittance',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rem.Remmit', verbose_name='Remittance Entry'),
        ),
        migrations.AlterField(
            model_name='requestpay',
            name='remittance',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rem.Remmit'),
        ),
    ]
