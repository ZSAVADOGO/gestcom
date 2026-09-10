from django.urls import path

from django.views.generic import RedirectView  # <-- IMPORT MANQUANT
from . import views


app_name = "communications"

urlpatterns = [
    path("", views.communique_dashboard, name="liste"),
    path("api/lister/", views.api_lister_communiques, name="api_lister"),
    
    # Actions séparées
    path('communiques/creer/', views.creer_communique, name='creer_communique'),
    #path('communiques/<int:communique_id>/modifier/', views.modifier_communique, name='modifier_communique'),
    path('<int:communique_id>/modifier/', views.modifier_communique, name='modifier_communique'),
]