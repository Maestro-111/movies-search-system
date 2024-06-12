from django.contrib.auth.decorators import login_required
from django.shortcuts import render,redirect
from django.urls import reverse
from django.http import HttpResponse,HttpResponseNotFound,HttpResponseRedirect

# Create your views here.


@login_required
def playlist_menu(request):

    return render(request, 'playlist/playlist_menu.html')

@login_required
def create_playlist(request):
    return HttpResponse("create_playlist")

@login_required
def view_playlists(request):
    return HttpResponse("view_playlists")
