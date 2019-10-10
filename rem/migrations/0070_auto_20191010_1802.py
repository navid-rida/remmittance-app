# Generated by Django 2.2.5 on 2019-10-10 12:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rem', '0069_auto_20191010_1631'),
    ]

    operations = [
        migrations.AddField(
            model_name='remmit',
            name='cash_incentive_status',
            field=models.CharField(choices=[('P', 'Paid'), ('H', 'Held'), ('U', 'Unpaid')], default='U', max_length=1, verbose_name='Cash Incentive Status'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='remittanceupdatehistory',
            name='remittance',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rem.Remmit', verbose_name='Remittance Entry'),
        ),
        migrations.AlterField(
            model_name='remmit',
            name='date_sending',
            field=models.DateField(verbose_name='Date of Sending Remittance'),
        ),
        migrations.AlterField(
            model_name='requestpay',
            name='remittance',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rem.Remmit'),
        ),
    ]
