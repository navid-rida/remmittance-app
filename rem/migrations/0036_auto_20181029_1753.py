# Generated by Django 2.0.7 on 2018-10-29 11:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rem', '0035_auto_20181029_1751'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='receiver',
            name='idexpire',
        ),
        migrations.RemoveField(
            model_name='receiver',
            name='idissue',
        ),
        migrations.RemoveField(
            model_name='receiver',
            name='idno',
        ),
        migrations.RemoveField(
            model_name='receiver',
            name='idtype',
        ),
        migrations.AlterField(
            model_name='requestpay',
            name='remittance',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rem.Remmit'),
        ),
    ]