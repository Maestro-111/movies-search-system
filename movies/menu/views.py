from django.shortcuts import render,redirect
from django.urls import reverse
from django.http import HttpResponse,HttpResponseNotFound,HttpResponseRedirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

def main_menu(request):
    return render(request, 'menu/menu.html')



def start_search(request):

    movie_search_url = reverse('movie_search')

    return redirect(movie_search_url)



def user_home(request):
    return render(request, "menu/user_home.html")



def page_not_found(request, exception):
    return HttpResponseNotFound("<h1> No such Page!! </h1>")



@csrf_exempt
def chat_bot_request(request):

    if request.method == 'POST':
        user_message = request.POST.get('chat_bot_request', '')

        response_message = f"Searching for movies related to: {user_message}"
        return JsonResponse({'response_message': response_message})

    return render(request, 'menu/menu.html')


