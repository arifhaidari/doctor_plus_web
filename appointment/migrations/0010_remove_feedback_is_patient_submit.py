# Generated by Django 3.2.3 on 2022-04-05 18:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('appointment', '0009_auto_20220325_1332'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='feedback',
            name='is_patient_submit',
        ),
    ]
