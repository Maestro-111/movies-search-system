from django.db import models
from django.urls import reverse
import pandas as pd
from django.conf import settings
from django.contrib.auth.models import User
from movie.models import Movie


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    review = models.TextField()

    class Meta:
        unique_together = ('user', 'movie')

    def __str__(self):
        return f'{self.user.username} - {self.movie.original_title}: {self.rating}'
