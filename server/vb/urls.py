from django.urls import path

from .views import home, school

urlpatterns = [
    path("<slug:slug>/", school, name="school"),
    path("", home),
]
