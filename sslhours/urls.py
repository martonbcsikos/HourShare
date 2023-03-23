from django.urls import path
from .views import home, cv, school, club, login


urlpatterns = [
    path("", home, name="home"),
    path("login/", login, name="login"),
    path("cv/<str:username>", cv, name="cv"),
    path("schools/<str:school_name>", school, name="school"),
    path("club/<str:club>", club, name="club"),
]
