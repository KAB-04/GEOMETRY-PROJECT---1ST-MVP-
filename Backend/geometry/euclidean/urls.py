from django.urls import path
from . import views


urlpatterns = [
    path("health/", views.health_api, name="health_api"),
    path("solve/", views.solve_api, name="solve_api"),
]
