from django.urls import path

from .views import (
    ResultatListView,
    ResultatDetailView,
)

app_name = "resultats"

urlpatterns = [
    path(
        "",
        ResultatListView.as_view(),
        name="liste"
    ),

    path(
        "<int:pk>/",
        ResultatDetailView.as_view(),
        name="detail"
    ),
]