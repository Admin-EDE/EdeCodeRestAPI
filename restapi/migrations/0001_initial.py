# Generated by Django 4.1 on 2022-08-05 20:30

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="QuerysRbds",
            fields=[
                (
                    "id",
                    models.IntegerField(
                        auto_created=True, primary_key=True, serialize=False
                    ),
                ),
                ("filename", models.CharField(max_length=20)),
                ("run", models.CharField(max_length=11)),
                ("otp", models.IntegerField()),
                ("rbd", models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name="Report",
            fields=[
                (
                    "id",
                    models.CharField(
                        auto_created=True,
                        max_length=32,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("rbd", models.IntegerField()),
                ("link", models.CharField(max_length=200)),
                ("run", models.CharField(max_length=11)),
                ("t_stamp", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="ResultReport",
            fields=[
                (
                    "id",
                    models.IntegerField(
                        auto_created=True, primary_key=True, serialize=False
                    ),
                ),
                ("report_id", models.CharField(max_length=32)),
                ("func_name", models.CharField(max_length=5)),
                ("result", models.CharField(max_length=9)),
            ],
        ),
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "id",
                    models.IntegerField(
                        auto_created=True, primary_key=True, serialize=False
                    ),
                ),
                ("username", models.CharField(max_length=11)),
                ("t_stamp", models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
