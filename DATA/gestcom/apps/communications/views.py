from django.db.models import Q
from django.views.generic import ListView, DetailView

from .models import Communique


class CommuniqueListView(ListView):
    """
    Liste des communiqués publiés.

    Permet :
    - recherche par titre/contenu
    - filtrage par type
    - pagination
    """

    model = Communique
    template_name = "communications/liste.html"
    context_object_name = "communiques"
    paginate_by = 12

    def get_queryset(self):
        queryset = (
            Communique.objects
            .filter(statut=Communique.Statut.PUBLIE)
            .order_by(
                "-est_a_la_une",
                "-ordre_affichage",
                "-date_publication"
            )
        )

        recherche = self.request.GET.get("q", "").strip()
        type_communique = self.request.GET.get("type", "").strip()

        if recherche:
            queryset = queryset.filter(
                Q(titre__icontains=recherche)
                | Q(resume__icontains=recherche)
                | Q(contenu__icontains=recherche)
            )

        if type_communique:
            queryset = queryset.filter(
                type=type_communique
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["types"] = Communique.Type.choices

        return context


class CommuniqueDetailView(DetailView):
    """
    Affichage d'un communiqué.
    """

    model = Communique
    template_name = "communications/detail.html"
    context_object_name = "communique"

    def get_queryset(self):
        return Communique.objects.filter(
            statut=Communique.Statut.PUBLIE
        )

    def get_object(self, queryset=None):
        communique = super().get_object(queryset)

        # Incrémentation simple du nombre de vues.
        Communique.objects.filter(
            pk=communique.pk
        ).update(
            nombre_vues=communique.nombre_vues + 1
        )

        return communique