from django.db import models
from movie.models import Movie
from django.contrib.auth.models import User  # Import the User model
from django.urls import reverse

class Playlist(models.Model):

    name = models.CharField(max_length=100)
    movie = models.ManyToManyField(Movie, related_name='playlist')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='playlists')

    def get_absolute_url(self):
        return reverse('view_single_playlist', kwargs={'playlist_id': self.id})

    def __str__(self):
        return self.name