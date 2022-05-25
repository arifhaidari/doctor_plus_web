# Generated by Django 3.2.3 on 2021-12-01 10:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0013_alter_user_avatar'),
        ('medicalrecord', '0005_alter_medicalrecords_title'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='medicalrecords',
            name='doctor',
        ),
        migrations.RemoveField(
            model_name='medicalrecords',
            name='doctor_access',
        ),
        migrations.AddField(
            model_name='medicalrecords',
            name='related_doctor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='related_doctor', to='user.doctor'),
        ),
        migrations.AddField(
            model_name='medicalrecords',
            name='shared_with',
            field=models.ManyToManyField(blank=True, to='user.Doctor'),
        ),
        migrations.AddField(
            model_name='medicalrecords',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
