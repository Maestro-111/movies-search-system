from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.forum_menu, name="forum_menu"),
    path('view_reviews/', views.view_reviews, name="view_reviews"),
    path('write_reviews/', views.write_review, name="write_review")
]