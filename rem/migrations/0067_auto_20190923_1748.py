# Generated by Django 2.2.5 on 2019-09-23 11:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rem', '0066_auto_20190916_1200'),
    ]

    operations = [
        migrations.AddField(
            model_name='remmit',
            name='booth',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='rem.Booth'),
        ),
        migrations.AlterField(
            model_name='booth',
            name='address',
            field=models.TextField(verbose_name='Address of the Booth'),
        ),
        migrations.AlterField(
            model_name='booth',
            name='branch',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rem.Branch', verbose_name='Branch Attached'),
        ),
        migrations.AlterField(
            model_name='booth',
            name='name',
            field=models.CharField(max_length=20, verbose_name='Name of the Booth'),
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
