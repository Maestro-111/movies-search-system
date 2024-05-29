from django.db import models
from django.urls import reverse
import pandas as pd
from django.conf import settings

class Movie(models.Model):
    movie_id = models.IntegerField(primary_key=True)
    original_title = models.CharField(max_length=255, null=True, blank=True)
    overview = models.TextField(null=True, blank=True)
    slug = models.SlugField(max_length=255, db_index=True, blank=True, default='')

    def get_absolute_url(self):
        return reverse('show_movie', kwargs={'movie_id': self.movie_id})

    class Meta:
        indexes = [
            models.Index(fields=['original_title'], name='original_title_idx'),
        ]

    def __str__(self):
        return str(self.slug)


df = pd.read_excel('C:/Users/La_Admin/Desktop/movies_metadata.xlsx',index_col=0)

def get_django_field_type(dtype):
    if pd.api.types.is_integer_dtype(dtype):
        return models.IntegerField(default=0)
    elif pd.api.types.is_float_dtype(dtype):
        return models.FloatField(default=0.0)
    elif pd.api.types.is_bool_dtype(dtype):
        return models.BooleanField(default=False)
    else:
        return models.CharField(max_length=255, default='')

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