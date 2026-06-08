from django.urls import path
from . import views


urlpatterns = [
    path("distance/", views.distance_api, name="distance_api"),
    path("circle-area/", views.circle_area_api, name="circle_area_api"),
]
