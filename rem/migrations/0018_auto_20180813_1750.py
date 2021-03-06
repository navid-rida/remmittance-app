# Generated by Django 2.0.7 on 2018-08-13 11:50

import django.core.validators
from django.db import migrations, models
import django.utils.timezone
import rem.validators


class Migration(migrations.Migration):

    dependencies = [
        ('rem', '0017_auto_20180805_1331'),
    ]

    operations = [
        migrations.AlterField(
            model_name='remmit',
            name='date',
            field=models.DateField(default=django.utils.timezone.now, validators=[rem.validators.validate_post_date], verbose_name='Remmittance Distribution Date'),
        ),
        migrations.AlterField(
            model_name='remmit',
            name='reference',
            field=models.CharField(max_length=16, validators=[django.core.validators.RegexValidator('^[0-9a-zA-Z]*$', 'Only Alphabet and numeric characters are allowed.')], verbose_name='Referene No.'),
        ),
    ]
