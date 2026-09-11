from django.urls import path
from . import views

app_name = "resultats"

urlpatterns = [
    #path("", views.communique_dashboard, name="liste"),
    path("", views.resultat_dashboard, name="resultat_dashboard"),
    path("api/lister/", views.api_lister_resultats, name="api_lister_resultats"),
]

""" from .views import (
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
] """