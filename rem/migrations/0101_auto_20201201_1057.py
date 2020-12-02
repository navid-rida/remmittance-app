# Generated by Django 2.2.5 on 2020-12-01 04:57

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rem', '0100_auto_20201126_1244'),
    ]

    operations = [
        migrations.AddField(
            model_name='exchangehouse',
            name='ac_no_branch',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='rem.Branch', verbose_name='Branch of CD Account/ GL'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='exchangehouse',
            name='ac_no',
            field=models.CharField(max_length=15, validators=[django.core.validators.RegexValidator('^[0-9]*$', 'Only numeric characters are allowed.')], verbose_name='Account no./ GL No. of Exchange House'),
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