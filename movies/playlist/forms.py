from django import forms
from .models import Playlist
from movie.models import Rating


class PlaylistForm(forms.ModelForm):
    class Meta:
        model = Playlist
        fields = ["name"]


class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ["rating"]
        widgets = {"rating": forms.NumberInput(attrs={"min": 1, "max": 5})}  # Assuming a rating scale of 1 to 5
