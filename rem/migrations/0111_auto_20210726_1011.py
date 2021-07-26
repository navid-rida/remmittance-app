# Generated by Django 2.2.5 on 2021-07-26 04:11

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rem', '0110_auto_20210401_1852'),
    ]

    operations = [
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
            model_name='remmit',
            name='currency',
            field=models.ForeignKey(default=17, on_delete=django.db.models.deletion.CASCADE, to='schedules.Currency', verbose_name='Currency of Remittance'),
        ),
        migrations.AlterField(
            model_name='remmit',
            name='sender_occupation',
            field=models.CharField(default='S', help_text='Service/ Business etc.', max_length=50, validators=[django.core.validators.RegexValidator('^[a-zA-Z]*$', 'Only alphabets are allowed.')], verbose_name='Occupation of Remitter'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='requestpay',
            name='remittance',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rem.Remmit'),
        ),
    ]
