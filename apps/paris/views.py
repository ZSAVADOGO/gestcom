from django.contrib import messages
from django.db.models import Q
from django.shortcuts import redirect
from django.views import View
from django.views.generic import ListView, DetailView
from django.shortcuts import render

from .models import Pari


class PariListView(ListView):
    """
    Liste des tickets.

    Cette vue est principalement destinée à l'interface
    d'administration/gestion.

    Elle ne doit pas exposer publiquement tous les tickets.
    """

    model = Pari
    template_name = "paris/liste.html"
    context_object_name = "paris"
    paginate_by = 30

    def get_queryset(self):
        return (
            Pari.objects
            .select_related(
                "course",
                "point_vente",
                "course__reunion"
            )
            .order_by("-date_prise")
        )


class PariDetailView(DetailView):
    """
    Détail d'un ticket.
    """

    model = Pari
    template_name = "paris/detail.html"
    context_object_name = "pari"

    def get_queryset(self):
        return (
            Pari.objects
            .select_related(
                "course",
                "point_vente",
                "course__reunion"
            )
        )


class VerificationTicketView(View):
    """
    Vérification publique d'un ticket.

    GET :
        affiche le formulaire.

    POST :
        recherche le ticket à partir de son numéro.
    """

    template_name = "paris/verification.html"

    def get(self, request, *args, **kwargs):

        return render(
            request,
            self.template_name
        )

    def post(self, request, *args, **kwargs):

        numero_ticket = request.POST.get(
            "numero_ticket",
            ""
        ).strip()

        if not numero_ticket:

            messages.error(
                request,
                "Veuillez saisir un numéro de ticket."
            )

            return render(
                request,
                self.template_name
            )

        try:

            pari = (
                Pari.objects
                .select_related(
                    "course",
                    "course__reunion",
                    "point_vente"
                )
                .get(
                    numero_ticket=numero_ticket
                )
            )

        except Pari.DoesNotExist:

            messages.error(
                request,
                "Aucun ticket ne correspond à ce numéro."
            )

            return render(
                request,
                self.template_name
            )

        return redirect(
            "paris:detail",
            pk=pari.pk
        )