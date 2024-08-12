from django.shortcuts import render,redirect
from django.urls import reverse
from django.http import HttpResponse,HttpResponseNotFound,HttpResponseRedirect
from .models import Review
from .forms import ReviewForm

def forum_menu(request):
    return render(request,'forum/forum_menu.html')


def write_review(request):
    return render(request,'forum/write_review.html')


def view_reviews(request):
    return render(request,'forum/view_reviews.html')