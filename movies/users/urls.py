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
    path("add_friend/", views.user_add_friend, name="add_friend"),
]
