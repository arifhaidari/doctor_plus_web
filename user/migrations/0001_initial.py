# Generated by Django 3.2 on 2021-05-10 07:02

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import user.models
import user.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('user_type', models.CharField(choices=[('PATIENT', 'Patient'), ('DOCTOR', 'Doctor'), ('RELATIVE', 'Relative'), ('ADMIN', 'Admin'), ('BLOGGER', 'Blogger'), ('HEALTHMINISTRY', 'HealthMinistry'), ('ADMINPLUS', 'Admin Plus')], default='PATIENT', max_length=50)),
                ('full_name', models.CharField(blank=True, max_length=255, null=True, validators=[user.validators.name])),
                ('rtl_full_name', models.CharField(blank=True, max_length=255, null=True, validators=[user.validators.name])),
                ('phone', models.CharField(max_length=255, unique=True, validators=[user.validators.phone_number])),
                ('email', models.CharField(blank=True, max_length=255, null=True, unique=True, validators=[django.core.validators.EmailValidator(message='Enter a valid email address.')])),
                ('date_of_birth', models.DateField(blank=True, null=True, validators=[user.validators.dob])),
                ('avatar', models.ImageField(default='user_avatar/default_avatar.png', upload_to=user.models.upload_user_avatar, validators=[user.validators.avatar_size, django.core.validators.FileExtensionValidator(['png', 'jpg', 'jpeg', 'tiff', 'tif', 'bmp'], message='Invalid Image extension.')])),
                ('active', models.BooleanField(default=False)),
                ('suspend', models.BooleanField(default=False)),
                ('gender', models.CharField(choices=[('MALE', 'Male'), ('FEMALE', 'Female')], default='MALE', max_length=15)),
                ('admin', models.BooleanField(default=False)),
                ('staff', models.BooleanField(default=False)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='BloodGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='DoctorTitle',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=120)),
                ('farsi_title', models.CharField(max_length=120)),
                ('pashto_title', models.CharField(max_length=120)),
            ],
        ),
        migrations.CreateModel(
            name='RelativeRelationships',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('relationship', models.CharField(max_length=16)),
                ('relationship_rtl', models.CharField(max_length=32, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='SpecialityCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('farsi_name', models.CharField(blank=True, max_length=255, null=True)),
                ('pashto_name', models.CharField(blank=True, max_length=255, null=True)),
                ('icon', models.ImageField(blank=True, null=True, upload_to=user.models.upload_speciality_icon)),
            ],
        ),
        migrations.CreateModel(
            name='Blogger',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='user.user')),
            ],
        ),
        migrations.CreateModel(
            name='HealthMinistry',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='user.user')),
            ],
        ),
        migrations.CreateModel(
            name='Patient',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='patient', serialize=False, to='user.user')),
                ('blood_group', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='user.bloodgroup')),
            ],
        ),
        migrations.CreateModel(
            name='Speciality',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
                ('farsi_name', models.CharField(blank=True, max_length=256, null=True)),
                ('pashto_name', models.CharField(blank=True, max_length=256, null=True)),
                ('speciality_category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.specialitycategory')),
            ],
            options={
                'verbose_name': 'Speciality',
                'verbose_name_plural': 'Specialities',
            },
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('farsi_name', models.CharField(max_length=128)),
                ('pashto_name', models.CharField(max_length=128)),
                ('speciality', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.speciality')),
            ],
        ),
        migrations.CreateModel(
            name='Condition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('farsi_name', models.CharField(max_length=128)),
                ('pashto_name', models.CharField(max_length=128)),
                ('speciality', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.speciality')),
            ],
        ),
        migrations.CreateModel(
            name='Relative',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='user.user')),
                ('blood_group', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='user.bloodgroup')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='relative', to='user.patient')),
                ('rel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.relativerelationships', verbose_name='Relationsship')),
            ],
        ),
        migrations.CreateModel(
            name='Doctor',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='doctor', serialize=False, to='user.user')),
                ('doctor_type', models.CharField(choices=[('VOLUNTEER', 'Volunteer'), ('ONPREMISE', 'On_Premise'), ('ONLINECONSULTANT', 'Online_Consultant')], default='VOLUNTEER', max_length=50)),
                ('doc_license_no', models.CharField(blank=True, max_length=150, null=True, unique=True)),
                ('fee', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('bio', models.TextField(blank=True, null=True)),
                ('farsi_bio', models.TextField(blank=True, null=True)),
                ('pashto_bio', models.TextField(blank=True, null=True)),
                ('professional_status', models.PositiveSmallIntegerField(choices=[(0, 'None'), (1, 'Pending'), (2, 'Active')], default=0)),
                ('condition', models.ManyToManyField(blank=True, to='user.Condition')),
                ('service', models.ManyToManyField(blank=True, to='user.Service')),
                ('speciality', models.ManyToManyField(blank=True, to='user.Speciality')),
                ('title', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='user.doctortitle')),
            ],
        ),
    ]
