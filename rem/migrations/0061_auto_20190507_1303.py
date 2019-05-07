# Generated by Django 2.0.7 on 2019-05-07 07:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('rem', '0060_auto_20190506_1537'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReceiverUpdateHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datecreate', models.DateTimeField(auto_now_add=True, verbose_name='Date of Editing')),
                ('ip', models.GenericIPAddressField(verbose_name='User IP Address')),
                ('createdby', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ('receiver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rem.Receiver', verbose_name='Receiver')),
            ],
        ),
        migrations.AlterField(
            model_name='requestpay',
            name='remittance',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rem.Remmit'),
        ),
    ]