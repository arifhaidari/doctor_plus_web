# Generated by Django 3.2.3 on 2022-03-15 16:29

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0022_alter_otpverification_timestamp'),
    ]

    operations = [
        migrations.AlterField(
            model_name='otpverification',
            name='timestamp',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
