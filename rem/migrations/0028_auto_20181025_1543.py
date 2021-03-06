# Generated by Django 2.0.7 on 2018-10-25 09:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rem', '0027_auto_20181022_1258'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='screenshot',
            field=models.ImageField(default='pic_folder/None/no-img.jpg', upload_to='images/%Y/%m/%d/'),
        ),
        migrations.AlterField(
            model_name='requestpay',
            name='remittance',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rem.Remmit'),
        ),
        migrations.AlterField(
            model_name='requestpay',
            name='status',
            field=models.CharField(choices=[('RV', 'Request staged for review'), ('RJ', 'Request rejected'), ('PD', 'Amount paid to customer')], default='RV', max_length=2, verbose_name='Request Status'),
        ),
    ]
