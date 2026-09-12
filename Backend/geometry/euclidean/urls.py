from django.urls import path
from . import views


urlpatterns = [
    path("health/", views.health_api, name="health_api"),
    path("solve/", views.solve_api, name="solve_api"),
    path("history/", views.history_api, name="history_api"),
    path("history/<int:pk>/", views.history_detail_api, name="history_detail_api"),
    path("topics/", views.topics_api, name="topics_api"),
]
