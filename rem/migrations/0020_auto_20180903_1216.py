# Generated by Django 2.0.7 on 2018-09-03 06:16

from django.db import migrations, models
import django.utils.timezone
import rem.validators


class Migration(migrations.Migration):

    dependencies = [
        ('rem', '0019_auto_20180816_1836'),
    ]

    operations = [
        migrations.AlterField(
            model_name='remmit',
            name='date',
            field=models.DateField(default=django.utils.timezone.now, validators=[rem.validators.validate_post_date], verbose_name='Remmittance Distribution Date'),
        ),
    ]
