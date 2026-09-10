from django.urls import path

from .views import (
    PointVenteListView,
    PointVenteDetailView,
)

app_name = "points_vente"

urlpatterns = [
    path(
        "",
        PointVenteListView.as_view(),
        name="liste"
    ),

    path(
        "<int:pk>/",
        PointVenteDetailView.as_view(),
        name="detail"
    ),
]