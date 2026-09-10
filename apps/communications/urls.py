from django.urls import path

from django.views.generic import RedirectView  # <-- IMPORT MANQUANT
from . import views


app_name = "communications"

urlpatterns = [
    path("", views.communique_dashboard, name="liste"),
    path("api/lister/", views.api_lister_communiques, name="api_lister"),
]