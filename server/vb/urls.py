from django.urls import path

from .views import check, home, school

urlpatterns = [
    path("<slug:slug>/check/", check, name="check"),
    path("<slug:slug>/", school, name="school"),
    path("", home),
]
