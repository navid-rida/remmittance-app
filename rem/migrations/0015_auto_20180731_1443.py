# Generated by Django 2.0.7 on 2018-07-31 08:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rem', '0014_auto_20180731_1431'),
    ]

    operations = [
        migrations.AlterField(
            model_name='branch',
            name='name',
            field=models.CharField(default='Principal', max_length=20, verbose_name='Name of The branch'),
        ),
    ]
