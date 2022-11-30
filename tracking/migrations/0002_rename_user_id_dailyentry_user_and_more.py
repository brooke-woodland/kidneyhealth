# Generated by Django 4.1.3 on 2022-11-30 20:39

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracking', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='dailyentry',
            old_name='user_ID',
            new_name='user',
        ),
        migrations.AlterField(
            model_name='dailyentry',
            name='entry_date',
            field=models.DateField(blank=True, default=datetime.date(2022, 11, 30)),
        ),
    ]
