# Generated by Django 2.2.5 on 2021-03-29 07:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rem', '0106_auto_20210324_1643'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cashincentive',
            name='entry_category',
            field=models.CharField(choices=[('P', 'Paid'), ('U', 'Not Paid'), ('NA', 'Not Applicable')], max_length=1, verbose_name='Payment Status'),
        ),
        migrations.AlterField(
            model_name='cashincentive',
            name='remittance',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rem.Remmit'),
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
