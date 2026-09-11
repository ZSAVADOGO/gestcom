from django.urls import path
from . import views



app_name = "points_vente"


urlpatterns = [
    path("", views.point_vente_dashboard, name="liste"),
    path('points-vente/', views.point_vente_dashboard, name='point_vente_dashboard'),
    path('points-vente/api/', views.api_lister_point_vente, name='api_lister_point_vente'),
    
    # Actions CRUD (remarquez l'utilisation de tirets pour correspondre au JS)
    path("points-vente/creer/", views.creer_point_vente, name="creer_point_vente"),
    path("points-vente/<int:point_vente_id>/modifier/", views.modifier_point_vente, name="modifier_point_vente"),
    
    
]

""" 
    path('points-vente/creer/', views.creer_point_vente, name='creer_point_vente'),
    path('points-vente/<int:point_vente_id>/modifier/', views.modifier_point_vente, name='modifier_point_vente'), """