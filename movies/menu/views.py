from django.shortcuts import render
from django.http import HttpResponse,HttpResponseNotFound,HttpResponseRedirect
# Create your views here.


def main_menu(reuqest):
    return HttpResponse("This is main menu page")