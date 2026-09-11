from django.views.generic import ListView, DetailView
from django.utils import timezone
from apps.hippisme.models import Course

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from .models import Resultat
from .services import lister_resultats


def resultat_dashboard(request):
    """
    Affichage principal et gestion des soumissions POST pour les résultats de courses.
    """
    # 1. GESTION DU POST (Saisie / Modification AJAX)        
    if request.method == "POST":
        # Récupération sécurisée et nettoyage des données (Nettoyage en ligne)
        res_id = request.POST.get("id")
        statut = request.POST.get("statut", Resultat.Statut.PROVISOIRE).upper()
        source = request.POST.get("source", Resultat.TypeSource.MANUEL).upper()
        
        non_partants = request.POST.get("non_partants", "00").strip()
        temps_course = request.POST.get("temps_course", "").strip()
        arrivee_brute = request.POST.get("arrivee_brute", "").strip()
        commentaire = request.POST.get("commentaire", "").strip()


        # Nettoyage de l'arrivée (conversion en liste)
        arrivee_liste = [
            x.strip() for x in arrivee_brute.replace(",", "-").split("-") if x.strip()
        ]

        try:
            if res_id:
                res_obj = Resultat.objects.get(id=res_id)
            else:
                res_obj = Resultat()

            res_obj.statut = statut
            res_obj.non_partants = non_partants
            res_obj.temps_course = temps_course
            res_obj.source = source
            res_obj.commentaire = commentaire
            res_obj.arrivee = arrivee_liste
            res_obj.save()

            return JsonResponse({
                "status": "success",
                "message": "Résultat enregistré avec succès !"
            }, status=200)

        except Exception as e:
            return JsonResponse({
                "status": "error",
                "erreur": f"Erreur lors de la sauvegarde : {str(e)}"
            }, status=400)

    # 2. GESTION DU GET (Affichage initial)
    q = request.GET.get("q", "").strip()
    statut_filtre = request.GET.get("statut", "").strip()
    
    date_unique = request.GET.get("date", "").strip()
    date_debut = request.GET.get("date_debut", "").strip() or date_unique
    date_fin = request.GET.get("date_fin", "").strip() or date_unique

    try:
        page = int(request.GET.get("page", 1))
    except ValueError:
        page = 1

    data = lister_resultats(
        recherche=q,
        statut=statut_filtre,
        date_debut=date_debut,
        date_fin=date_fin,
        page=page,
        page_size=12
    )

    contexte = {
        "statuts_resultat": Resultat.Statut.choices,
        "resultats_initiaux": data.get("objects", []),
        "pagination_initiale": data.get("pagination", {}),
        "objects": data.get("objects", []),
    }


    return render(request, "resultats/resultat_dashboard.html", contexte)


@require_GET
def api_lister_resultats(request):
    """
    Endpoint JSON pour recherche, filtrage et pagination dynamique.
    """
    try:
        page = int(request.GET.get("page", 1))
        page_size = int(request.GET.get("page_size", 12))
    except ValueError:
        page, page_size = 1, 12

    date_unique = request.GET.get("date", "").strip()
    date_debut = request.GET.get("date_debut", "").strip() or date_unique
    date_fin = request.GET.get("date_fin", "").strip() or date_unique

    data = lister_resultats(
        recherche=request.GET.get("q", "").strip(),
        statut=request.GET.get("statut", "").strip(),
        date_debut=date_debut,
        date_fin=date_fin,
        page=page,
        page_size=page_size
    )
    return JsonResponse(data, status=200)

""" 
@require_GET
def resultat_dashboard(request):
#    Affichage principal du tableau de bord des résultats de courses.
    q = request.GET.get("q", "").strip()
    statut_filtre = request.GET.get("statut", "").strip()
    date_debut = request.GET.get("date_debut", "").strip()
    date_fin = request.GET.get("date_fin", "").strip()

    try:
        page = int(request.GET.get("page", 1))
    except ValueError:
        page = 1

    data = lister_resultats(
        recherche=q,
        statut=statut_filtre,
        date_debut=date_debut,
        date_fin=date_fin,
        page=page,
        page_size=12
    )

    contexte = {
        "statuts_resultat": Resultat.Statut.choices,
        "resultats_initiaux": data.get("objects", []),
        "pagination_initiale": data.get("pagination", {}),
        "objects": data.get("objects", []),
    }

    return render(request, "resultats/resultat_dashboard.html", contexte)


@require_GET
def api_lister_resultats(request):
#    Endpoint JSON pour recherche, filtrage et pagination dynamique.
    try:
        page = int(request.GET.get("page", 1))
        page_size = int(request.GET.get("page_size", 12))
    except ValueError:
        page, page_size = 1, 12

    data = lister_resultats(
        recherche=request.GET.get("q", "").strip(),
        statut=request.GET.get("statut", "").strip(),
        date_debut=request.GET.get("date_debut", "").strip(),
        date_fin=request.GET.get("date_fin", "").strip(),
        page=page,
        page_size=page_size
    )

    return JsonResponse(data, status=200)
 """