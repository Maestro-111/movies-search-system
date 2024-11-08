# Generated by Django 5.1.1 on 2024-11-08 05:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("movie", "0003_movieembedding"),
    ]

    operations = [
        migrations.CreateModel(
            name="Actors",
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
                ("actor_name", models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="MovieActor",
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
                    "character_name",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "actor",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="movie.actors"
                    ),
                ),
                (
                    "movie",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="movie.movie"
                    ),
                ),
            ],
            options={
                "unique_together": {("movie", "actor")},
            },
        ),
    ]