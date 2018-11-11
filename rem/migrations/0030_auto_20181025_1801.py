# Generated by Django 2.0.7 on 2018-10-25 12:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rem', '0029_auto_20181025_1759'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='screenshot',
            field=models.ImageField(default='images/None/no-img.jpg', upload_to='images/%Y/%m/%d/'),
        ),
        migrations.AlterField(
            model_name='requestpay',
            name='remittance',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rem.Remmit'),
        ),
    ]
