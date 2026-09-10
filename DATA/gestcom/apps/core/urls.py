# apps/core/urls.py
from django.urls import path
from .views import actualiser_donnees_view

# ⚠️ Gardez 'resultats' si vous voulez conserver le namespace des templates ({% url 'resultats:actualiser_donnees' %})
# Ou changez pour 'core' si vous souhaitez centraliser sous le namespace 'core' ({% url 'core:actualiser_donnees' %})
app_name = 'core'

urlpatterns = [
    path('actualiser/', actualiser_donnees_view, name='actualiser_donnees'),
]