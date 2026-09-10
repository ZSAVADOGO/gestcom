from django.db.models import Q
from django.views.generic import ListView, DetailView

from .models import PointVente


class PointVenteListView(ListView):
    """
    Liste des points de vente actifs.

    Recherche :
    - nom
    - ville
    - quartier
    - adresse
    - code
    """

    model = PointVente
    template_name = "points_vente/liste.html"
    context_object_name = "points_vente"
    paginate_by = 20

    def get_queryset(self):
        queryset = (
            PointVente.objects
            .filter(est_actif=True)
            .order_by(
                "ville",
                "quartier",
                "nom"
            )
        )

        recherche = self.request.GET.get(
            "q",
            ""
        ).strip()

        type_point = self.request.GET.get(
            "type",
            ""
        ).strip()

        if recherche:
            queryset = queryset.filter(
                Q(nom__icontains=recherche)
                | Q(code__icontains=recherche)
                | Q(ville__icontains=recherche)
                | Q(quartier__icontains=recherche)
                | Q(adresse__icontains=recherche)
            )

        if type_point:
            queryset = queryset.filter(
                type=type_point
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["types"] = PointVente.Type.choices

        return context


class PointVenteDetailView(DetailView):
    """
    Détail d'un point de vente actif.
    """

    model = PointVente
    template_name = "points_vente/detail.html"
    context_object_name = "point"

    def get_queryset(self):
        return PointVente.objects.filter(
            est_actif=True
        )