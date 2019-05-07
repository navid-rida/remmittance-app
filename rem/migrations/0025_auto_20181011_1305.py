# Generated by Django 2.0.7 on 2018-10-11 07:05

from django.db import migrations, models
import django.db.models.deletion
import rem.validators


class Migration(migrations.Migration):

    dependencies = [
        ('rem', '0024_auto_20180930_1456'),
    ]

    operations = [
        migrations.RenameField(
            model_name='remmit',
            old_name='reciever',
            new_name='receiver',
        ),
        migrations.AlterField(
            model_name='receiver',
            name='cell',
            field=models.CharField(max_length=14, unique=True, validators=[rem.validators.validate_mobile], verbose_name='Cell number of Receiver'),
        ),
        migrations.AlterField(
            model_name='requestpay',
            name='remittance',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rem.Remmit'),
        ),
    ]