from django.urls import path
from . import views

urlpatterns = [path("", views.main_menu, name="main_menu"), path("start_search/", views.start_search, name="start_search")]
