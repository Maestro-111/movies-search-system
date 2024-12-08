from django.urls import path
from . import views


app_name = "users"


urlpatterns = [
    path("login/", views.login_user, name="login"),
    path("register/", views.register_user, name="register_user"),
    path("logout/", views.logout_user, name="logout"),
    path("change_password/", views.change_password, name="change_password"),
]
