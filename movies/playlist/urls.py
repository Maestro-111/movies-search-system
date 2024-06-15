from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.playlist_menu, name="playlist_menu"),
    path('create_playlist/', views.create_playlist, name="create_playlist"),
    path('view_playlists/', views.view_playlists, name="view_playlists"),
    path('view_playlist/<int:playlist_id>/', views.view_single_playlist, name="view_single_playlist"),
    path('add_movie_to_playlist/<int:movie_id>/', views.add_movie_to_playlist, name="add_movie_to_playlist"),
    path('remove_movie_from_playlist/<int:playlist_id>/<int:movie_id>/', views.remove_movie_from_playlist, name='remove_movie_from_playlist'),
    path('delete_playlist/<int:playlist_id>/', views.delete_playlist, name='delete_playlist')
]