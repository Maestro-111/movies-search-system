from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.playlist_menu, name="playlist_menu"),
    path('create_playlist/', views.create_playlist, name="create_playlist"),
    path('view_playlists/', views.view_playlists, name="view_playlists")
]