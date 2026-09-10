from django.urls import path

from django.views.generic import RedirectView  # <-- IMPORT MANQUANT

from .views import (
    CommuniqueListView,
    CommuniqueDetailView,
)

app_name = "communications"

urlpatterns = [
    path(
        "",
        CommuniqueListView.as_view(),
        name="liste"
    ),

    path(
        "<int:pk>/",
        CommuniqueDetailView.as_view(),
        name="detail"
    ),
]