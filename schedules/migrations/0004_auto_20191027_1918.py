# Generated by Django 2.2.5 on 2019-10-27 13:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedules', '0003_auto_20191023_1322'),
    ]

    operations = [
        migrations.AlterField(
            model_name='currency',
            name='name',
            field=models.CharField(max_length=50, verbose_name='Name of Currenct'),
        ),
    ]