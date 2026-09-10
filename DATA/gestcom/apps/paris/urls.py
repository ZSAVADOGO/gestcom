from django.urls import path

from .views import (
    PariListView,
    PariDetailView,
    VerificationTicketView,
)

app_name = "paris"

urlpatterns = [

    path(
        "",
        PariListView.as_view(),
        name="liste"
    ),

    path(
        "verification/",
        VerificationTicketView.as_view(),
        name="verification"
    ),

    path(
        "<int:pk>/",
        PariDetailView.as_view(),
        name="detail"
    ),
]