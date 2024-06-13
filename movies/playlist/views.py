from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponse,HttpResponseNotFound,HttpResponseRedirect
from .models import Playlist

# Create your views here.


# ADD: param to show movie in get_abs_url for movie to pass corresponding url to go back


@login_required
def playlist_menu(request):

    return render(request, 'playlist/playlist_menu.html')

@login_required
def create_playlist(request):

    # if request in GET, just render the template
    # if POST then get the name of the playlist and create entry in table and redirect to previous

    if request.method == 'POST':
        play_list_name = request.POST.get('play_list_name')

        #if play_list_name

        existing_playlist = Playlist.objects.filter(name=play_list_name, user=request.user).first()

        if existing_playlist:
            return render(request, 'playlist/create_playlist.html',
                          {
                              'error_message': 'A playlist with this name already exists.'
                          }
                          )
        else:
            Playlist.objects.create(name=play_list_name, user=request.user)
            return HttpResponseRedirect(reverse('main_menu'))

    else:
        return render(request, 'playlist/create_playlist.html')


@login_required
def view_playlists(request):

    playlists = Playlist.objects.filter(user=request.user)



    context = {
        "playlists":playlists
    }

    return render(request, 'playlist/view_all_playlists.html',context)

@login_required
def delete_playlist(request):
    return HttpResponse("delete_playlist")

@login_required
def view_single_playlist(request, playlist_id:int):



    playlist = get_object_or_404(Playlist, id=playlist_id)
    movies = playlist.movie.all()

    context = {
        "movies":movies,
        "playlist":playlist
    }

    print(movies)


    return render(request, 'playlist/view_single_playlist.html',context)



@login_required
def add_movie_to_playlist(request, movie_id):
    return HttpResponse(f"We want to add {movie_id} to playlist!")
