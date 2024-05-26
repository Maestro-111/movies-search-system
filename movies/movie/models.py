from django.db import models
from django.urls import reverse

class Movie(models.Model):
    movie_id = models.IntegerField(primary_key=True)
    original_title = models.CharField(max_length=255, null=True, blank=True)
    overview = models.TextField(null=True, blank=True)
    slug = models.SlugField(max_length=255, db_index=True, blank=True, default='')

    def get_absolute_url(self):
        return reverse('show_movie', kwargs={'movie_id': self.movie_id})

    def __str__(self):
        return str(self.slug)
