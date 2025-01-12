from django.urls import path
from . import views


app_name = "users"


urlpatterns = [
    path("user_home/", views.user_home, name="user_home"),
    path("login/", views.login_user, name="login"),
    path("register/", views.register_user, name="register_user"),
    path("logout/", views.logout_user, name="logout"),
    path("change_password/", views.change_password, name="change_password"),
    path("view_friends/", views.user_view_friends, name="view_friends"),
    path("user_search/", views.user_search, name="user_search"),
    path("view_user_profile/<str:username>/", views.show_user, name="show_user"),
    path("add_friend/<int:friend_id>/", views.user_add_friends, name="user_add_friends"),
    path("user_summary/", views.user_summary, name="user_summary"),
]