# Generated by Django 3.2.3 on 2022-03-30 13:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('appointment', '0009_auto_20220325_1332'),
        ('notification', '0004_auto_20220328_1822'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='notification',
            name='doctor',
        ),
        migrations.RemoveField(
            model_name='notification',
            name='patient',
        ),
        migrations.AddField(
            model_name='notification',
            name='appt',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='appointment.appointment'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='category',
            field=models.CharField(blank=True, choices=[('appt_cancelation', 'Appt Cancelation'), ('review_reply', 'Review Reply'), ('review', 'Review')], max_length=25, null=True),
        ),
    ]
