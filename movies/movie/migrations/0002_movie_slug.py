# Generated by Django 4.2.1 on 2024-05-25 19:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movie', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='movie',
            name='slug',
            field=models.SlugField(blank=True, default='', max_length=255),
        ),
    ]
