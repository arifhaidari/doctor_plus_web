# Generated by Django 3.2.3 on 2021-08-14 12:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('medicalrecord', '0004_auto_20210813_1600'),
    ]

    operations = [
        migrations.AlterField(
            model_name='medicalrecords',
            name='title',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Title'),
        ),
    ]
