from django.shortcuts import render,redirect
from django.urls import reverse
from django.http import HttpResponse,HttpResponseNotFound,HttpResponseRedirect

# Create your views here.

def forum_menu(request):
    return render(request,'forum/forum_menu.html')


def write_review(request):
    return HttpResponse("writing")


def view_reviews(request):
    return render(request,'forum/view_reviews.html')