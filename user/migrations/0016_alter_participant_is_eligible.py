# Generated by Django 4.0.5 on 2023-03-25 10:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0015_participant_is_eligible'),
    ]

    operations = [
        migrations.AlterField(
            model_name='participant',
            name='is_eligible',
            field=models.IntegerField(default=0),
        ),
    ]
