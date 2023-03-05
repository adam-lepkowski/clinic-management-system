# Generated by Django 4.1.5 on 2023-03-05 08:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import main.utils


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0004_appointment_appointment_unique_doctor_appointment_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='doctor',
            field=models.ForeignKey(default='DOCTOR REMOVED', on_delete=django.db.models.deletion.SET_DEFAULT, to=settings.AUTH_USER_MODEL, validators=[main.validators.is_physician]),
        ),
    ]
