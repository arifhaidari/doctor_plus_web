# Generated by Django 3.2.3 on 2021-05-25 11:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0004_alter_user_phone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='timestamp',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
