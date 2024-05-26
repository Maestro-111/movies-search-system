
from django.urls import path, re_path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.enter_query, name='enter_query'),
    path('search/', views.movie_search, name='movie_search'),
    path('show_movie/<int:movie_id>/', views.show_movie, name='show_movie'),
]