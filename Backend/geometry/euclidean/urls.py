from django.urls import path
from . import views


urlpatterns = [
    path("solve/", views.solve_api, name="solve_api"),
]
