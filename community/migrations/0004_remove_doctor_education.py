# Generated by Django 5.0.6 on 2024-05-22 21:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0003_alter_audience_gender_alter_doctor_gender'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='doctor',
            name='education',
        ),
    ]
