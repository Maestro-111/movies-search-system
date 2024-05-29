from django.shortcuts import render,redirect
from django.urls import reverse
from django.http import HttpResponse,HttpResponseNotFound,HttpResponseRedirect




def main_menu(reuqest):
    return render(reuqest, 'menu/menu.html')



def start_search(request):

    movie_search_url = reverse('movie_search')

    return redirect(movie_search_url)


def page_not_found(request, exception):
    return HttpResponseNotFound("<h1> No such Page!! </h1>")