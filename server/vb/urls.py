from django.urls import path

from .views import check, finish_check, home, rules, school, validate_email

app_name = "vb"
urlpatterns = [
    path("rules/", rules, name="rules"),
    path("<slug:slug>/v/<str:token>/", validate_email, name="validate_email"),
    path("<slug:slug>/check/finish/", finish_check, name="finish_check"),
    path("<slug:slug>/check/", check, name="check"),
    path("<slug:slug>/", school, name="school"),
    path("", home, name="home"),
]
