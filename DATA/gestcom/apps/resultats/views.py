from django.views.generic import ListView, DetailView
from django.utils import timezone
from apps.hippisme.models import Course


from .models import Resultat

class ResultatListView(ListView):
    """
    Liste des résultats disponibles.
    """

    model = Resultat
    template_name = "resultats/liste.html"
    context_object_name = "resultats"
    paginate_by = 20

    def get_queryset(self):
        return (
            Resultat.objects.select_related(
                "course", "course__reunion", "course__reunion__hippodrome"
            )
            .filter(
                statut__in=[
                    Resultat.Statut.PROVISOIRE,
                    Resultat.Statut.OFFICIEL,
                ]
            )
            .order_by("-date_publication", "-course__reunion__date_reunion")
        )


class ResultatDetailView(DetailView):
    """
    Détail d'un résultat.
    """

    model = Resultat
    template_name = "resultats/detail.html"
    context_object_name = "resultat"

    def get_queryset(self):
        return Resultat.objects.select_related(
            "course", "course__reunion", "course__reunion__hippodrome"
        ).filter(
            statut__in=[
                Resultat.Statut.PROVISOIRE,
                Resultat.Statut.OFFICIEL,
            ]
        )
