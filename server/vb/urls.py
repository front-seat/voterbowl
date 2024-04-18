from django.urls import path

from .views import check, finish_check, home, school, verify_email

app_name = "vb"
urlpatterns = [
    path("<slug:slug>/verify/<str:token>/", verify_email, name="verify_email"),
    path("<slug:slug>/check/finish/", finish_check, name="finish_check"),
    path("<slug:slug>/check/", check, name="check"),
    path("<slug:slug>/", school, name="school"),
    path("", home),
]
