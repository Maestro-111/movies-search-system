# Generated by Django 5.1.1 on 2024-11-20 18:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("movie", "0006_delete_movieembedding"),
    ]

    operations = [
        migrations.AlterField(
            model_name="movie",
            name="original_title",
            field=models.CharField(blank=True, max_length=512, null=True),
        ),
        migrations.AlterField(
            model_name="movie",
            name="slug",
            field=models.SlugField(blank=True, default="", max_length=512),
        ),
        migrations.AlterField(
            model_name="movie",
            name="tagline",
            field=models.CharField(blank=True, max_length=512, null=True),
        ),
    ]