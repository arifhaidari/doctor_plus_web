# Generated by Django 3.2.3 on 2021-06-10 06:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0005_alter_user_timestamp'),
    ]

    operations = [
        migrations.AlterField(
            model_name='doctor',
            name='professional_status',
            field=models.BooleanField(default=False),
        ),
    ]
