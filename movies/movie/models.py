from django.db import models
from django.urls import reverse
import pandas as pd
from django.conf import settings
from django.contrib.auth.models import User
import json

class Movie(models.Model):

    movie_id = models.IntegerField(primary_key=True)
    original_title = models.CharField(max_length=512, null=True, blank=True)
    overview = models.TextField(null=True, blank=True)
    slug = models.SlugField(max_length=512, db_index=True, blank=True, default='')
    tagline = models.CharField(max_length=512, blank=True,null=True)
    year = models.IntegerField(blank=True,null=True)
    genres = models.ManyToManyField("MovieGenres",blank=True,related_name='genres')
    languages = models.ManyToManyField("MovieLanguages",blank=True,related_name='languages')
    ratings = models.ManyToManyField(User, through='Rating', related_name='rated_movies')
    actors = models.ManyToManyField("Actors", through='MovieActor', related_name='actors', blank=True)

    def get_absolute_url(self):
        return reverse('show_movie', kwargs={'movie_id': self.movie_id})

    class Meta:
        indexes = [
            models.Index(fields=['original_title'], name='original_title_idx'),
        ]

    def __str__(self):
        return str(self.slug)


class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = ('user', 'movie')

    def __str__(self):
        return f'{self.user.username} - {self.movie.original_title}: {self.rating}'


df = pd.read_excel(settings.METADATA_PATH,index_col=0)

def get_django_field_type(dtype):
    if pd.api.types.is_integer_dtype(dtype):
        return models.IntegerField(default=0)
    elif pd.api.types.is_float_dtype(dtype):
        return models.FloatField(default=0.0)
    elif pd.api.types.is_bool_dtype(dtype):
        return models.BooleanField(default=False)
    else:
        return models.CharField(max_length=512, default='')

# Create MovieBase class
class MovieMetaDataBase(models.Model):
    class Meta:
        abstract = True

# Dynamically add fields to the MovieBase model
for column_name, dtype in df.dtypes.items():
    field = get_django_field_type(dtype)
    MovieMetaDataBase.add_to_class(column_name, field)

# Create the final Movie model
class MovieMetaData(MovieMetaDataBase):
    movie = models.OneToOneField(Movie, on_delete=models.CASCADE, primary_key=True)

class Actors(models.Model):

    actor_name = models.CharField(max_length=512, null=True, blank=True)

    def __str__(self):
        return self.actor_name

class MovieActor(models.Model):

    movie = models.ForeignKey('Movie', on_delete=models.CASCADE)
    actor = models.ForeignKey('Actors', on_delete=models.CASCADE)
    character_name = models.CharField(max_length=512, null=True, blank=True)

    class Meta:
        unique_together = ('movie', 'actor')

class MovieGenres(models.Model):

    genre_id = models.IntegerField(primary_key=True)
    genre = models.CharField(max_length=512)


    class Meta:
        indexes = [
            models.Index(fields=['genre_id'], name='genre_id_idx'),
        ]

    def __str__(self):
        return str(self.genre)

class MovieLanguages(models.Model):

    language_id = models.IntegerField(primary_key=True)
    language = models.CharField(max_length=512)


    class Meta:
        indexes = [
            models.Index(fields=['language_id'], name='language_id_idx'),
        ]

    def __str__(self):
        return str(self.language)