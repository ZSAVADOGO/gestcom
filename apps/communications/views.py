from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_GET, require_http_methods
from django.utils import timezone
from django.http import JsonResponse, HttpResponseBadRequest
from django.utils.dateparse import parse_datetime
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Communique
# Importez votre fonction de service
from .services import lister_communiques


def communique_dashboard(request):
    """
    Vue principale : Gère à la fois l'affichage/filtrage (GET) 
    et l'enregistrement/modification (POST).
    """
    # --------------------------------------------------------------------------
    # 1. TRAITEMENT DE L'AJOUT ET DE LA MODIFICATION (POST)
    # --------------------------------------------------------------------------
    if request.method == "POST":
        communique_id = request.POST.get("id", "").strip()
        titre = request.POST.get("titre", "").strip()
        type_comm = request.POST.get("type", "").strip()
        statut = request.POST.get("statut", "").strip()
        resume = request.POST.get("resume", "").strip()
        contenu = request.POST.get("contenu", "").strip()
        date_pub_str = request.POST.get("date_publication", "").strip()
        est_a_la_une = request.POST.get("est_a_la_une") in ["true", "on", "1", True]
        image_file = request.FILES.get("image")

        # Validation des champs requis
        if not titre or not contenu or not type_comm or not statut:
            return HttpResponseBadRequest("Certains champs obligatoires sont manquants.")

        # Conversion de la date au format Django
        date_publication = parse_datetime(date_pub_str) if date_pub_str else None

        # Si un ID existe, il s'agit d'une modification, sinon c'est une création
        if communique_id:
            communique = get_object_or_404(Communique, id=communique_id)
        else:
            communique = Communique()

        # Affectation des valeurs
        communique.titre = titre
        communique.type = type_comm
        communique.statut = statut
        communique.resume = resume
        communique.contenu = contenu
        communique.est_a_la_une = est_a_la_une

        if date_publication:
            communique.date_publication = date_publication
            
        if image_file:
            communique.image = image_file

        communique.save()

        # Réponse JSON pour le fetch AJAX de votre JS
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"status": "success", "id": communique.id}, status=200)

    # --------------------------------------------------------------------------
    # 2. AFFICHAGE DU TABLEAU DE BORD ET FILTRAGE (GET)
    # --------------------------------------------------------------------------
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





# @login_required
""" @require_GET
def api_lister_communiques(request):

    #API JSON servant pour le filtrage et la pagination dynamique (AJAX / Alpine.js).
    Query params : q, type, page, page_size
    
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
        page=page,
        page_size=page_size,
    )
    
    return JsonResponse(resultat, status=200) """
