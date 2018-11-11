# Generated by Django 2.0.7 on 2018-10-16 09:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rem', '0025_auto_20181011_1305'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='payment',
            name='comment',
        ),
        migrations.AddField(
            model_name='requestpay',
            name='comment',
            field=models.TextField(null=True, verbose_name='Reason for rejection or any other remarks'),
        ),
        migrations.AddField(
            model_name='requestpay',
            name='status',
            field=models.CharField(choices=[('RV', 'Request staged for review'), ('RJ', 'Request rejected'), ('PD', 'Amount paid to customer')], default='RV', max_length=2, verbose_name=' Request Status'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='status',
            field=models.CharField(choices=[('U', 'Payment yet to be settled'), ('S', 'Payment settled')], default='U', max_length=1, verbose_name='Status'),
        ),
        migrations.AlterField(
            model_name='requestpay',
            name='remittance',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rem.Remmit'),
        ),
    ]
