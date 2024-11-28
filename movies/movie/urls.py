from django.urls import path
from . import views

urlpatterns = [
    path("", views.enter_query, name="enter_query"),
    path("chatbot/", views.chat_bot_request, name="chat_bot_request"),
    path("search/", views.movie_search, name="movie_search"),
    path("show_movie/<int:movie_id>/", views.show_movie, name="show_movie"),
]
