# Generated by Django 4.0.5 on 2023-03-28 18:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0018_participant_is_eligible'),
    ]

    operations = [
        migrations.AddField(
            model_name='participant',
            name='longitudinal_enrollment_status',
            field=models.IntegerField(default=0),
        ),
    ]