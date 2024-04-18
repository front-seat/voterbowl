from django.urls import path

from .views import check, finish_check, home, school

urlpatterns = [
    path("<slug:slug>/check/finish/", finish_check, name="finish_check"),
    path("<slug:slug>/check/", check, name="check"),
    path("<slug:slug>/", school, name="school"),
    path("", home),
]
