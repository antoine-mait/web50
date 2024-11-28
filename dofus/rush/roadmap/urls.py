from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("builds/", views.builds, name="builds"),
    path("roadmap/", views.roadmap, name="roadmap"),
    path("spreadsheet/", views.spreadsheet, name="spreadsheet"),
]