# Generated by Django 5.1.1 on 2025-01-24 15:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("movie", "0011_topicdescription"),
        ("playlist", "0002_playlist_user"),
    ]

    operations = [
        migrations.AddField(
            model_name="usertopicdistribution",
            name="playlist",
            field=models.ForeignKey(
                default=None,
                on_delete=django.db.models.deletion.CASCADE,
                to="playlist.playlist",
            ),
        ),
    ]
