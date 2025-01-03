# Generated by Django 4.2.1 on 2024-06-03 20:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Movie",
            fields=[
                ("movie_id", models.IntegerField(primary_key=True, serialize=False)),
                (
                    "original_title",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("overview", models.TextField(blank=True, null=True)),
                ("slug", models.SlugField(blank=True, default="", max_length=255)),
                ("tagline", models.CharField(blank=True, max_length=255, null=True)),
                ("year", models.IntegerField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="MovieMetaData",
            fields=[
                ("budget", models.FloatField(default=0.0)),
                ("popularity", models.FloatField(default=0.0)),
                ("year", models.FloatField(default=0.0)),
                ("revenue", models.FloatField(default=0.0)),
                ("runtime", models.FloatField(default=0.0)),
                ("vote_average", models.FloatField(default=0.0)),
                ("In Production", models.IntegerField(default=0)),
                ("Planned", models.IntegerField(default=0)),
                ("Post Production", models.IntegerField(default=0)),
                ("Released", models.IntegerField(default=0)),
                ("Rumored", models.IntegerField(default=0)),
                ("ab", models.IntegerField(default=0)),
                ("af", models.IntegerField(default=0)),
                ("ar", models.IntegerField(default=0)),
                ("bg", models.IntegerField(default=0)),
                ("bn", models.IntegerField(default=0)),
                ("bo", models.IntegerField(default=0)),
                ("bs", models.IntegerField(default=0)),
                ("ca", models.IntegerField(default=0)),
                ("cn", models.IntegerField(default=0)),
                ("cs", models.IntegerField(default=0)),
                ("da", models.IntegerField(default=0)),
                ("de", models.IntegerField(default=0)),
                ("el", models.IntegerField(default=0)),
                ("en", models.IntegerField(default=0)),
                ("es", models.IntegerField(default=0)),
                ("et", models.IntegerField(default=0)),
                ("eu", models.IntegerField(default=0)),
                ("fa", models.IntegerField(default=0)),
                ("fi", models.IntegerField(default=0)),
                ("fr", models.IntegerField(default=0)),
                ("he", models.IntegerField(default=0)),
                ("hi", models.IntegerField(default=0)),
                ("hr", models.IntegerField(default=0)),
                ("hu", models.IntegerField(default=0)),
                ("id", models.IntegerField(default=0)),
                ("is", models.IntegerField(default=0)),
                ("it", models.IntegerField(default=0)),
                ("ja", models.IntegerField(default=0)),
                ("ko", models.IntegerField(default=0)),
                ("ku", models.IntegerField(default=0)),
                ("lv", models.IntegerField(default=0)),
                ("mk", models.IntegerField(default=0)),
                ("ml", models.IntegerField(default=0)),
                ("mr", models.IntegerField(default=0)),
                ("nb", models.IntegerField(default=0)),
                ("nl", models.IntegerField(default=0)),
                ("no", models.IntegerField(default=0)),
                ("pa", models.IntegerField(default=0)),
                ("pl", models.IntegerField(default=0)),
                ("ps", models.IntegerField(default=0)),
                ("pt", models.IntegerField(default=0)),
                ("ro", models.IntegerField(default=0)),
                ("ru", models.IntegerField(default=0)),
                ("sk", models.IntegerField(default=0)),
                ("sl", models.IntegerField(default=0)),
                ("sm", models.IntegerField(default=0)),
                ("sr", models.IntegerField(default=0)),
                ("sv", models.IntegerField(default=0)),
                ("ta", models.IntegerField(default=0)),
                ("te", models.IntegerField(default=0)),
                ("th", models.IntegerField(default=0)),
                ("tl", models.IntegerField(default=0)),
                ("tr", models.IntegerField(default=0)),
                ("uk", models.IntegerField(default=0)),
                ("ur", models.IntegerField(default=0)),
                ("vi", models.IntegerField(default=0)),
                ("wo", models.IntegerField(default=0)),
                ("xx", models.IntegerField(default=0)),
                ("zh", models.IntegerField(default=0)),
                ("Japanese", models.IntegerField(default=0)),
                ("Swahili", models.IntegerField(default=0)),
                ("German", models.IntegerField(default=0)),
                ("Hindi", models.IntegerField(default=0)),
                ("Irish", models.IntegerField(default=0)),
                ("Icelandic", models.IntegerField(default=0)),
                ("Norwegian Bokmål", models.IntegerField(default=0)),
                ("Vietnamese", models.IntegerField(default=0)),
                ("Urdu", models.IntegerField(default=0)),
                ("Bambara", models.IntegerField(default=0)),
                ("Zulu", models.IntegerField(default=0)),
                ("Hausa", models.IntegerField(default=0)),
                ("Ukrainian", models.IntegerField(default=0)),
                ("Maltese", models.IntegerField(default=0)),
                ("Punjabi", models.IntegerField(default=0)),
                ("Fulfulde", models.IntegerField(default=0)),
                ("Swedish", models.IntegerField(default=0)),
                ("Lithuanian", models.IntegerField(default=0)),
                ("Bosnian", models.IntegerField(default=0)),
                ("French", models.IntegerField(default=0)),
                ("Wolof", models.IntegerField(default=0)),
                ("English", models.IntegerField(default=0)),
                ("Kazakh", models.IntegerField(default=0)),
                ("Galician", models.IntegerField(default=0)),
                ("Welsh", models.IntegerField(default=0)),
                ("Slovenian", models.IntegerField(default=0)),
                ("Albanian", models.IntegerField(default=0)),
                ("Russian", models.IntegerField(default=0)),
                ("Finnish", models.IntegerField(default=0)),
                ("Norwegian", models.IntegerField(default=0)),
                ("Hungarian", models.IntegerField(default=0)),
                ("Romanian", models.IntegerField(default=0)),
                ("Thai", models.IntegerField(default=0)),
                ("Georgian", models.IntegerField(default=0)),
                ("Dutch", models.IntegerField(default=0)),
                ("Slovak", models.IntegerField(default=0)),
                ("Korean", models.IntegerField(default=0)),
                ("Czech", models.IntegerField(default=0)),
                ("Hebrew", models.IntegerField(default=0)),
                ("Bengali", models.IntegerField(default=0)),
                ("Kinyarwanda", models.IntegerField(default=0)),
                ("Telugu", models.IntegerField(default=0)),
                ("Basque", models.IntegerField(default=0)),
                ("Arabic", models.IntegerField(default=0)),
                ("Bulgarian", models.IntegerField(default=0)),
                ("Uzbek", models.IntegerField(default=0)),
                ("Spanish", models.IntegerField(default=0)),
                ("Greek", models.IntegerField(default=0)),
                ("Cantonese", models.IntegerField(default=0)),
                ("Italian", models.IntegerField(default=0)),
                ("Polish", models.IntegerField(default=0)),
                ("Latin", models.IntegerField(default=0)),
                ("Croatian", models.IntegerField(default=0)),
                ("Latvian", models.IntegerField(default=0)),
                ("Somali", models.IntegerField(default=0)),
                ("Persian", models.IntegerField(default=0)),
                ("Turkish", models.IntegerField(default=0)),
                ("Serbian", models.IntegerField(default=0)),
                ("Catalan", models.IntegerField(default=0)),
                ("Tamil", models.IntegerField(default=0)),
                ("Malay", models.IntegerField(default=0)),
                ("Afrikaans", models.IntegerField(default=0)),
                ("Indonesian", models.IntegerField(default=0)),
                ("Danish", models.IntegerField(default=0)),
                ("Belarusian", models.IntegerField(default=0)),
                ("Portuguese", models.IntegerField(default=0)),
                ("Pashto", models.IntegerField(default=0)),
                ("Estonian", models.IntegerField(default=0)),
                ("Azerbaijani", models.IntegerField(default=0)),
                ("Mandarin", models.IntegerField(default=0)),
                ("Esperanto", models.IntegerField(default=0)),
                ("War", models.IntegerField(default=0)),
                ("Romance", models.IntegerField(default=0)),
                ("Adventure", models.IntegerField(default=0)),
                ("Sentai Filmworks", models.IntegerField(default=0)),
                ("The Cartel", models.IntegerField(default=0)),
                ("Drama", models.IntegerField(default=0)),
                ("Documentary", models.IntegerField(default=0)),
                ("Odyssey Media", models.IntegerField(default=0)),
                ("Mystery", models.IntegerField(default=0)),
                ("Family", models.IntegerField(default=0)),
                ("Animation", models.IntegerField(default=0)),
                ("Aniplex", models.IntegerField(default=0)),
                ("Telescene Film Group Productions", models.IntegerField(default=0)),
                ("Foreign", models.IntegerField(default=0)),
                ("BROSTA TV", models.IntegerField(default=0)),
                ("Action", models.IntegerField(default=0)),
                ("Fantasy", models.IntegerField(default=0)),
                ("Rogue State", models.IntegerField(default=0)),
                ("Horror", models.IntegerField(default=0)),
                ("Pulser Productions", models.IntegerField(default=0)),
                ("Music", models.IntegerField(default=0)),
                ("Crime", models.IntegerField(default=0)),
                ("Carousel Productions", models.IntegerField(default=0)),
                ("TV Movie", models.IntegerField(default=0)),
                ("Science Fiction", models.IntegerField(default=0)),
                ("Western", models.IntegerField(default=0)),
                ("Vision View Entertainment", models.IntegerField(default=0)),
                (
                    "Mardock Scramble Production Committee",
                    models.IntegerField(default=0),
                ),
                ("Comedy", models.IntegerField(default=0)),
                ("History", models.IntegerField(default=0)),
                ("GoHands", models.IntegerField(default=0)),
                ("Thriller", models.IntegerField(default=0)),
                (
                    "movie",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        primary_key=True,
                        serialize=False,
                        to="movie.movie",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="MovieLanguages",
            fields=[
                ("language_id", models.IntegerField(primary_key=True, serialize=False)),
                ("language", models.CharField(max_length=255)),
            ],
            options={
                "indexes": [models.Index(fields=["language_id"], name="language_id_idx")],
            },
        ),
        migrations.CreateModel(
            name="MovieGenres",
            fields=[
                ("genre_id", models.IntegerField(primary_key=True, serialize=False)),
                ("genre", models.CharField(max_length=255)),
            ],
            options={
                "indexes": [models.Index(fields=["genre_id"], name="genre_id_idx")],
            },
        ),
        migrations.AddField(
            model_name="movie",
            name="genres",
            field=models.ManyToManyField(blank=True, related_name="genres", to="movie.moviegenres"),
        ),
        migrations.AddField(
            model_name="movie",
            name="languages",
            field=models.ManyToManyField(blank=True, related_name="languages", to="movie.movielanguages"),
        ),
        migrations.AddIndex(
            model_name="movie",
            index=models.Index(fields=["original_title"], name="original_title_idx"),
        ),
    ]
