from django.urls import path

from . import views


app_name = "main"

urlpatterns = [
    path("", views.MainView.as_view(), name="main"),
    path("schedule/search", views.ScheduleSearchView.as_view(), name="schedule"),
    path(
        "schedule/search-results",
        views.ScheduleListView.as_view(),
        name="search_results")
]
