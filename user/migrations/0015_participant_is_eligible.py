# Generated by Django 4.0.5 on 2023-03-25 05:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0014_no_change'),
    ]

    operations = [
        migrations.AddField(
            model_name='participant',
            name='is_eligible',
            field=models.BooleanField(default=False),
        ),
    ]
