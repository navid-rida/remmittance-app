# Generated by Django 2.2.16 on 2022-06-06 07:16

from django.db import migrations, models
import rem.validators


class Migration(migrations.Migration):

    dependencies = [
        ('schedules', '0012_auto_20220606_1113'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rate',
            name='rate',
            field=models.DecimalField(decimal_places=4, max_digits=7, validators=[rem.validators.validate_neg], verbose_name='Exchange Rate in BDT'),
        ),
    ]