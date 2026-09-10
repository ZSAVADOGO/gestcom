"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path 
from django.views.generic import RedirectView  # <-- IMPORT MANQUANT

urlpatterns = [
    path('admin/', admin.site.urls),
    
# Redirige la page d'accueil vers /communications/
    path("", RedirectView.as_view(pattern_name="communications:liste", permanent=False)),
    path('core/', include('apps.core.urls', namespace='core')),
    path(
        "communications/",
        include(
            "apps.communications.urls",
            namespace="communications"
        )
    ),

    path(
        "points_vente/",
        include(
            "apps.points_vente.urls",
            namespace="points_vente"
        )
    ),

    path(
        "resultats/",
        include(
            "apps.resultats.urls",
            namespace="resultats"
        )
    ),

    path(
        "paris/",
        include(
            "apps.paris.urls",
            namespace="paris"
        )
    ),
    
    path(
        "hippisme/",
        include("apps.hippisme.urls", namespace="hippisme")
    ),

]
