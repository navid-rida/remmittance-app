# Generated by Django 2.0.7 on 2019-01-09 04:53

from django.db import migrations, models
import django.db.models.deletion
import rem.validators


class Migration(migrations.Migration):

    dependencies = [
        ('rem', '0056_auto_20190108_1730'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='cell',
            field=models.CharField(max_length=14, validators=[rem.validators.validate_mobile], verbose_name='Cell number of Receiver'),
        ),
        migrations.AlterField(
            model_name='requestpay',
            name='remittance',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rem.Remmit'),
        ),
    ]
