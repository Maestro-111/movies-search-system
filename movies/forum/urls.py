from django.urls import path
from . import views


urlpatterns = [
    path("", views.forum_menu, name="forum_menu"),
    path("view_reviews/", views.view_reviews, name="view_reviews"),
    path(
        "view_single_review/<int:review_id>/",
        views.view_single_review,
        name="view_single_review",
    ),
    path("write_reviews/<int:movie_id>/", views.write_review, name="write_review"),
]
