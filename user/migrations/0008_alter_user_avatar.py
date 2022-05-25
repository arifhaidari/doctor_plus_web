# Generated by Django 3.2.3 on 2021-06-10 11:35

import django.core.validators
from django.db import migrations, models
import user.models
import user.validators


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0007_auto_20210610_1425'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='avatar',
            field=models.ImageField(default='user_avatar/default_avatar3.png', upload_to=user.models.upload_user_avatar, validators=[user.validators.avatar_size, django.core.validators.FileExtensionValidator(['png', 'jpg', 'jpeg', 'tiff', 'tif', 'bmp'], message='Invalid Image extension.')]),
        ),
    ]
