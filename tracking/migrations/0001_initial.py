# Generated by Django 4.1.3 on 2022-11-30 17:40

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Comorbidity",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("comorbid_description", models.CharField(max_length=20)),
            ],
            options={"db_table": "comorbidity",},
        ),
        migrations.CreateModel(
            name="DailyEntry",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "entry_date",
                    models.DateField(blank=True, default=datetime.date.today),
                ),
                (
                    "water_intake_liters",
                    models.DecimalField(decimal_places=2, max_digits=4),
                ),
            ],
            options={"db_table": "daily_entry",},
        ),
        migrations.CreateModel(
            name="Food",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("food_description", models.CharField(max_length=50)),
                ("brand_name", models.CharField(blank=True, max_length=40)),
                (
                    "serving_size",
                    models.DecimalField(blank=True, decimal_places=2, max_digits=6),
                ),
                ("serving_size_unit", models.CharField(blank=True, max_length=2)),
                ("protien_g", models.DecimalField(decimal_places=2, max_digits=6)),
                ("phosphorus_mg", models.DecimalField(decimal_places=2, max_digits=6)),
                ("potassium_mg", models.DecimalField(decimal_places=2, max_digits=6)),
                ("sodium_mg", models.DecimalField(decimal_places=2, max_digits=6)),
            ],
            options={"db_table": "food",},
        ),
        migrations.CreateModel(
            name="Race",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("race_description", models.CharField(max_length=10)),
            ],
            options={"db_table": "race",},
        ),
        migrations.CreateModel(
            name="Profile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("gender", models.CharField(max_length=2)),
                ("phone", models.CharField(max_length=12)),
                ("weight", models.DecimalField(decimal_places=2, max_digits=5)),
                ("height", models.DecimalField(decimal_places=2, max_digits=5)),
                ("birth_date", models.DateField()),
                (
                    "comorbidity_ID",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="tracking.comorbidity",
                    ),
                ),
                (
                    "race_ID",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="tracking.race",
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"db_table": "user",},
        ),
        migrations.CreateModel(
            name="Lab",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("lab_date", models.DateField(blank=True, default=datetime.date.today)),
                ("blood_pressure", models.DecimalField(decimal_places=2, max_digits=5)),
                (
                    "potassium_level",
                    models.DecimalField(decimal_places=2, max_digits=5),
                ),
                (
                    "phosphorous_level",
                    models.DecimalField(decimal_places=2, max_digits=5),
                ),
                ("sodium_level", models.DecimalField(decimal_places=2, max_digits=5)),
                (
                    "creatinine_level",
                    models.DecimalField(decimal_places=2, max_digits=5),
                ),
                ("albumin_level", models.DecimalField(decimal_places=2, max_digits=5)),
                (
                    "blood_sugar_level",
                    models.DecimalField(decimal_places=2, max_digits=5),
                ),
                (
                    "user_ID",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"db_table": "lab",},
        ),
        migrations.CreateModel(
            name="FoodHistory",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("quantity", models.DecimalField(decimal_places=2, max_digits=4)),
                (
                    "entry_ID",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="tracking.dailyentry",
                    ),
                ),
                (
                    "food_ID",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="tracking.food"
                    ),
                ),
            ],
            options={"db_table": "food_history",},
        ),
        migrations.AddField(
            model_name="dailyentry",
            name="foods",
            field=models.ManyToManyField(
                through="tracking.FoodHistory", to="tracking.food"
            ),
        ),
        migrations.AddField(
            model_name="dailyentry",
            name="user_ID",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
    ]
