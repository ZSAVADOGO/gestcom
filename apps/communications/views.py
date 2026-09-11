from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from django.utils import timezone
from django.http import JsonResponse, HttpResponseBadRequest
from django.utils.dateparse import parse_datetime
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Communique
# Importez votre fonction de service
from .services import lister_communiques

def _extraire_et_sauvegarder_communique(request, instance=None):
    titre = request.POST.get("titre", "").strip()
    type_comm = request.POST.get("type", "").strip()
    statut = request.POST.get("statut", "").strip()
    resume = request.POST.get("resume", "").strip()
    contenu = request.POST.get("contenu", "").strip()
    date_pub_str = request.POST.get("date_publication", "").strip()
    est_a_la_une = request.POST.get("est_a_la_une") in ["true", "on", "1", True]
    image_file = request.FILES.get("image")

    if not titre or not contenu or not type_comm or not statut:
        return None, "Certains champs obligatoires sont manquants."

    communique = instance if instance else Communique()

    communique.titre = titre
    communique.type = type_comm
    communique.statut = statut
    communique.resume = resume
    communique.contenu = contenu
    communique.est_a_la_une = est_a_la_une

    if date_pub_str:
        communique.date_publication = parse_datetime(date_pub_str)

    if image_file:
        communique.image = image_file

    communique.save()
    return communique, None


@require_POST
def creer_communique(request):
    communique, erreur = _extraire_et_sauvegarder_communique(request)

    if erreur:
        return JsonResponse({"erreur": erreur}, status=400)

    return JsonResponse({
        "status": "success",
        "id": communique.id,
        "message": "Le communiqué a été créé avec succès."
    }, status=201)


@require_POST
def modifier_communique(request, communique_id):
    communique_existant = get_object_or_404(Communique, id=communique_id)
    communique, erreur = _extraire_et_sauvegarder_communique(request, instance=communique_existant)

    if erreur:
        return JsonResponse({"erreur": erreur}, status=400)

    return JsonResponse({
        "status": "success",
        "id": communique.id,
        "message": "Le communiqué a été mis à jour avec succès."
    }, status=200)

# ------------------------------------------------------------------------------
# 1. VUE : AFFICHAGE & FILTRAGE DUDASHBOARD (GET)
# ------------------------------------------------------------------------------

@require_GET
def communique_dashboard(request):
    """
    Vue réservée exclusivement à l'affichage et au filtrage des communiqués.
    """
    q = request.GET.get("q", "").strip()
    type_filtre = request.GET.get("type", "").strip()
    statut_filtre = request.GET.get("statut", "").strip()
    date_debut = request.GET.get("date_debut", "").strip()
    date_fin = request.GET.get("date_fin", "").strip()

    try:
        page = int(request.GET.get("page", 1))
    except ValueError:
        page = 1

    resultat = lister_communiques(
        recherche=q,
        type_communique=type_filtre,
        statut=statut_filtre,
        date_debut=date_debut,
        date_fin=date_fin,
        page=page,
        page_size=12
    )

    contexte = {
        "types_communique": Communique.Type.choices,
        "statuts_communique": Communique.Statut.choices,
        "resultats_initiaux": resultat.get("resultats", []),
        "pagination_initiale": resultat.get("pagination", {}),
        "communiques": resultat.get("objects", []),
    }
    
    return render(request, "communications/com_dahboard.html", contexte)


@require_GET
def api_lister_communiques(request):
    """
    API JSON pour la recherche, le filtrage multi-critères et la pagination dynamique.
    """
    try:
        page = int(request.GET.get("page", 1))
    except ValueError:
        page = 1

    try:
        page_size = int(request.GET.get("page_size", 12))
    except ValueError:
        page_size = 12

    resultat = lister_communiques(
        recherche=request.GET.get("q", "").strip(),
        type_communique=request.GET.get("type", "").strip(),
        statut=request.GET.get("statut", "").strip(),
        date_debut=request.GET.get("date_debut", "").strip(),
        date_fin=request.GET.get("date_fin", "").strip(),
        page=page,
        page_size=page_size,
    )
    
    return JsonResponse(resultat, status=200)



