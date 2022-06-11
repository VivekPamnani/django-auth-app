# Generated by Django 4.0.3 on 2022-06-11 08:35

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_alter_participant_last_visit_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='participant',
            name='last_visit',
            field=models.DateTimeField(default=datetime.datetime(1000, 1, 1, 0, 0)),
        ),
        migrations.AlterField(
            model_name='participant',
            name='visit_time_1',
            field=models.DateTimeField(default=datetime.datetime(1000, 1, 1, 0, 0)),
        ),
        migrations.AlterField(
            model_name='participant',
            name='visit_time_2',
            field=models.DateTimeField(default=datetime.datetime(1000, 1, 1, 0, 0)),
        ),
        migrations.AlterField(
            model_name='participant',
            name='visit_time_3',
            field=models.DateTimeField(default=datetime.datetime(1000, 1, 1, 0, 0)),
        ),
        migrations.AlterField(
            model_name='participant',
            name='visit_time_4',
            field=models.DateTimeField(default=datetime.datetime(1000, 1, 1, 0, 0)),
        ),
        migrations.AlterField(
            model_name='participant',
            name='visit_time_5',
            field=models.DateTimeField(default=datetime.datetime(1000, 1, 1, 0, 0)),
        ),
        migrations.AlterField(
            model_name='participant',
            name='visit_time_6',
            field=models.DateTimeField(default=datetime.datetime(1000, 1, 1, 0, 0)),
        ),
    ]
