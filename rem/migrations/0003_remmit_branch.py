# Generated by Django 2.0.7 on 2018-07-15 11:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rem', '0002_auto_20180715_1708'),
    ]

    operations = [
        migrations.AddField(
            model_name='remmit',
            name='branch',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='rem.Branch'),
            preserve_default=False,
        ),
    ]
