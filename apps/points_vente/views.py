from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.utils.dateparse import parse_date
from .models import PointVente  # Adaptez l'import selon votre application
from django.core.paginator import Paginator


def _extraire_et_sauvegarder_point_vente(request, instance=None):
    code = request.POST.get("code", "").strip()
    nom = request.POST.get("nom", "").strip()
    type_pv = request.POST.get("type", "").strip()
    ville = request.POST.get("ville", "Ouagadougou").strip()
    quartier = request.POST.get("quartier", "").strip()
    adresse = request.POST.get("adresse", "").strip()
    telephone = request.POST.get("telephone", "").strip()
    email = request.POST.get("email", "").strip()
    description = request.POST.get("description", "").strip()
    date_ouverture_str = request.POST.get("date_ouverture", "").strip()
    latitude_str = request.POST.get("latitude", "").strip()
    longitude_str = request.POST.get("longitude", "").strip()

    est_actif = request.POST.get("est_actif") in ["true", "on", "1", True]
    est_principal = request.POST.get("est_principal") in ["true", "on", "1", True]

    if not code or not nom or not type_pv:
        return None, "Les champs Code, Nom et Type sont obligatoires."

    code_exists = PointVente.objects.filter(code=code)
    if instance:
        code_exists = code_exists.exclude(id=instance.id)
    if code_exists.exists():
        return None, f"Un point de vente avec le code '{code}' existe déjà."

    point_vente = instance if instance else PointVente()
    point_vente.code = code
    point_vente.nom = nom
    point_vente.type = type_pv
    point_vente.ville = ville
    point_vente.quartier = quartier
    point_vente.adresse = adresse
    point_vente.telephone = telephone
    point_vente.email = email
    point_vente.description = description
    point_vente.est_actif = est_actif
    point_vente.est_principal = est_principal

    point_vente.date_ouverture = parse_date(date_ouverture_str) if date_ouverture_str else None

    try:
        point_vente.latitude = float(latitude_str) if latitude_str else None
        point_vente.longitude = float(longitude_str) if longitude_str else None
    except ValueError:
        return None, "Les coordonnées géographiques sont invalides."

    point_vente.save()
    return point_vente, None


""" 
def _extraire_et_sauvegarder_point_vente(request, instance=None):
    #Fonction utilitaire interne pour extraire les données POST
    #et sauvegarder l'instance du Point de Vente.

    code = request.POST.get("code", "").strip()
    nom = request.POST.get("nom", "").strip()
    type_pv = request.POST.get("type", "").strip()
    ville = request.POST.get("ville", "Ouagadougou").strip()
    quartier = request.POST.get("quartier", "").strip()
    adresse = request.POST.get("adresse", "").strip()
    telephone = request.POST.get("telephone", "").strip()
    email = request.POST.get("email", "").strip()
    description = request.POST.get("description", "").strip()
    date_ouverture_str = request.POST.get("date_ouverture", "").strip()

    latitude_str = request.POST.get("latitude", "").strip()
    longitude_str = request.POST.get("longitude", "").strip()

    est_actif = request.POST.get("est_actif") in ["true", "on", "1", True]
    est_principal = request.POST.get("est_principal") in ["true", "on", "1", True]

    # Validation des champs obligatoires
    if not code or not nom or not type_pv:
        return None, "Les champs Code, Nom et Type sont obligatoires."

    # Vérification d'unicité du code lors de la création ou si le code change
    code_exists = PointVente.objects.filter(code=code)
    if instance:
        code_exists = code_exists.exclude(id=instance.id)
    if code_exists.exists():
        return None, f"Un point de vente avec le code '{code}' existe déjà."

    point_vente = instance if instance else PointVente()

    point_vente.code = code
    point_vente.nom = nom
    point_vente.type = type_pv
    point_vente.ville = ville
    point_vente.quartier = quartier
    point_vente.adresse = adresse
    point_vente.telephone = telephone
    point_vente.email = email
    point_vente.description = description
    point_vente.est_actif = est_actif
    point_vente.est_principal = est_principal

    if date_ouverture_str:
        point_vente.date_ouverture = parse_date(date_ouverture_str)
    else:
        point_vente.date_ouverture = None

    if latitude_str:
        try:
            point_vente.latitude = float(latitude_str)
        except ValueError:
            return None, "La latitude doit être un nombre valide."
    else:
        point_vente.latitude = None

    if longitude_str:
        try:
            point_vente.longitude = float(longitude_str)
        except ValueError:
            return None, "La longitude doit être un nombre valide."
    else:
        point_vente.longitude = None

    point_vente.save()
    return point_vente, None """


# ------------------------------------------------------------------------------
# 1. VUE : DASHBOARD PRINCIPAL (GET)
# ------------------------------------------------------------------------------ 
@require_GET
def point_vente_dashboard(request):
    q = request.GET.get("q", "").strip()
    type_filtre = request.GET.get("type", "").strip()
    ville_filtre = request.GET.get("ville", "").strip()
    statut_filtre = request.GET.get("statut", "").strip()

    try:
        page = int(request.GET.get("page", 1))
        page_size = int(request.GET.get("page_size", 7))
    except ValueError:
        page, page_size = 1, 7

    qs = PointVente.objects.all().order_by("-id")

    if q:
        qs = qs.filter(nom__icontains=q) | qs.filter(code__icontains=q)
    if type_filtre:
        qs = qs.filter(type=type_filtre)
    if ville_filtre:
        qs = qs.filter(ville__icontains=ville_filtre)
    if statut_filtre == "actif":
        qs = qs.filter(est_actif=True)
    elif statut_filtre == "inactif":
        qs = qs.filter(est_actif=False)

    paginator = Paginator(qs, page_size)
    page_obj = paginator.get_page(page)

    resultats_initiaux = [
        {
            "id": pv.id,
            "code": pv.code,
            "nom": pv.nom,
            "type": pv.type,
            "type_label": pv.get_type_display(),
            "ville": pv.ville,
            "quartier": pv.quartier,
            "adresse": pv.adresse,
            "telephone": pv.telephone,
            "email": pv.email,
            "description": pv.description,
            "est_actif": pv.est_actif,
            "est_principal": pv.est_principal,
            "date_ouverture": pv.date_ouverture.strftime("%Y-%m-%d") if pv.date_ouverture else "",
            "latitude": str(pv.latitude) if pv.latitude else "",
            "longitude": str(pv.longitude) if pv.longitude else "",
        }
        for pv in page_obj.object_list
    ]

    pagination_initiale = {
        "page_courante": page_obj.number,
        "total_pages": paginator.num_pages,
        "total_elements": paginator.count,
        "taille_page": page_size,
        "a_precedent": page_obj.has_previous(),
        "a_suivant": page_obj.has_next(),
    }

    contexte = {
        "types_point_vente": PointVente.Type.choices,
        "resultats_initiaux": resultats_initiaux,
        "pagination_initiale": pagination_initiale,
    }

    return render(request, "points_vente/point_vente_dashboard.html", contexte)

@require_GET
def api_lister_point_vente(request):
    q = request.GET.get("q", "").strip()
    type_filtre = request.GET.get("type", "").strip()
    ville_filtre = request.GET.get("ville", "").strip()
    statut_filtre = request.GET.get("statut", "").strip()

    try:
        page = int(request.GET.get("page", 1))
        page_size = int(request.GET.get("page_size", 7))
    except ValueError:
        page, page_size = 1, 7

    qs = PointVente.objects.all().order_by("-id")

    if q:
        qs = qs.filter(nom__icontains=q) | qs.filter(code__icontains=q)
    if type_filtre:
        qs = qs.filter(type=type_filtre)
    if ville_filtre:
        qs = qs.filter(ville__icontains=ville_filtre)
    if statut_filtre == "actif":
        qs = qs.filter(est_actif=True)
    elif statut_filtre == "inactif":
        qs = qs.filter(est_actif=False)

    paginator = Paginator(qs, page_size)
    page_obj = paginator.get_page(page)

    data = [
        {
            "id": pv.id,
            "code": pv.code,
            "nom": pv.nom,
            "type": pv.type,
            "type_label": pv.get_type_display(),
            "ville": pv.ville,
            "quartier": pv.quartier,
            "adresse": pv.adresse,
            "telephone": pv.telephone,
            "email": pv.email,
            "description": pv.description,
            "est_actif": pv.est_actif,
            "est_principal": pv.est_principal,
            "date_ouverture": pv.date_ouverture.strftime("%Y-%m-%d") if pv.date_ouverture else "",
            "latitude": str(pv.latitude) if pv.latitude else "",
            "longitude": str(pv.longitude) if pv.longitude else "",
        }
        for pv in page_obj.object_list
    ]

    pagination = {
        "page_courante": page_obj.number,
        "total_pages": paginator.num_pages,
        "total_elements": paginator.count,
        "taille_page": page_size,
        "a_precedent": page_obj.has_previous(),
        "a_suivant": page_obj.has_next(),
    }

    return JsonResponse({"status": "success", "objects": data, "pagination": pagination}, status=200)


@require_POST
def creer_point_vente(request):
    pv, erreur = _extraire_et_sauvegarder_point_vente(request)
    if erreur:
        return JsonResponse({"erreur": erreur}, status=400)
    return JsonResponse({"status": "success", "id": pv.id, "message": "Le point de vente a été créé avec succès."}, status=201)


@require_POST
def modifier_point_vente(request, point_vente_id):
    pv_existant = get_object_or_404(PointVente, id=point_vente_id)
    pv, erreur = _extraire_et_sauvegarder_point_vente(request, instance=pv_existant)
    if erreur:
        return JsonResponse({"erreur": erreur}, status=400)
    return JsonResponse({"status": "success", "id": pv.id, "message": "Le point de vente a été mis à jour avec succès."}, status=200)

""" 
@require_GET
def point_vente_dashboard(request):
   # Vue du tableau de bord des points de vente avec données initiales
   # prêtes pour l'hydratation JS.
    q = request.GET.get("q", "").strip()
    type_filtre = request.GET.get("type", "").strip()
    ville_filtre = request.GET.get("ville", "").strip()
    statut_filtre = request.GET.get("statut", "").strip()

    try:
        page = int(request.GET.get("page", 1))
    except ValueError:
        page = 1

    try:
        page_size = int(request.GET.get("page_size", 7))
    except ValueError:
        page_size = 7

    qs = PointVente.objects.all().order_by("-id")

    if q:
        qs = qs.filter(nom__icontains=q) | qs.filter(code__icontains=q)
    if type_filtre:
        qs = qs.filter(type=type_filtre)
    if ville_filtre:
        qs = qs.filter(ville__icontains=ville_filtre)
    if statut_filtre == "actif":
        qs = qs.filter(est_actif=True)
    elif statut_filtre == "inactif":
        qs = qs.filter(est_actif=False)

    paginator = Paginator(qs, page_size)
    page_obj = paginator.get_page(page)

    resultats_initiaux = [
        {
            "id": pv.id,
            "code": pv.code,
            "nom": pv.nom,
            "type": pv.type,
            "type_label": pv.get_type_display(),
            "ville": pv.ville,
            "quartier": pv.quartier,
            "adresse": pv.adresse,
            "telephone": pv.telephone,
            "email": pv.email,
            "description": pv.description,
            "est_actif": pv.est_actif,
            "est_principal": pv.est_principal,
            "date_ouverture": pv.date_ouverture.strftime("%Y-%m-%d") if pv.date_ouverture else "",
            "latitude": str(pv.latitude) if pv.latitude else "",
            "longitude": str(pv.longitude) if pv.longitude else "",
        }
        for pv in page_obj.object_list
    ]

    pagination_initiale = {
        "page_courante": page_obj.number,
        "total_pages": paginator.num_pages,
        "total_elements": paginator.count,
        "taille_page": page_size,
        "a_precedent": page_obj.has_previous(),
        "a_suivant": page_obj.has_next(),
    }

    contexte = {
        "types_point_vente": PointVente.Type.choices,
        "resultats_initiaux": resultats_initiaux,
        "pagination_initiale": pagination_initiale,
    }

    return render(request, "points_vente/point_vente_dashboard.html", contexte) """

""" 
# ------------------------------------------------------------------------------
# 2. VUE : API LISTER (GET AJAX)
# ------------------------------------------------------------------------------
@require_GET
def api_lister_point_vente(request):
    #API JSON pour la recherche, le filtrage et la pagination dynamique.
    q = request.GET.get("q", "").strip()
    type_filtre = request.GET.get("type", "").strip()
    ville_filtre = request.GET.get("ville", "").strip()

    qs = PointVente.objects.all().order_by("-id")
    if q:
        qs = qs.filter(nom__icontains=q) | qs.filter(code__icontains=q)
    if type_filtre:
        qs = qs.filter(type=type_filtre)
    if ville_filtre:
        qs = qs.filter(ville__icontains=ville_filtre)

    data = [
        {
            "id": pv.id,
            "code": pv.code,
            "nom": pv.nom,
            "type": pv.type,
            "type_label": pv.get_type_display(),
            "ville": pv.ville,
            "quartier": pv.quartier,
            "telephone": pv.telephone,
            "est_actif": pv.est_actif,
            "est_principal": pv.est_principal,
        }
        for pv in qs
    ]

    return JsonResponse({"status": "success", "objects": data}, status=200)


# ------------------------------------------------------------------------------
# 3. VUE : CRÉATION (POST)
# ------------------------------------------------------------------------------
@require_POST
def creer_point_vente(request):
#    Création d'un nouveau point de vente.
    pv, erreur = _extraire_et_sauvegarder_point_vente(request)

    if erreur:
        return JsonResponse({"erreur": erreur}, status=400)

    return JsonResponse(
        {
            "status": "success",
            "id": pv.id,
            "message": "Le point de vente a été créé avec succès."
        },
        status=201
    )


# ------------------------------------------------------------------------------
# 4. VUE : MODIFICATION (POST)
# ------------------------------------------------------------------------------
@require_POST
def modifier_point_vente(request, point_vente_id):
    Modification d'un point de vente existant.
    pv_existant = get_object_or_404(PointVente, id=point_vente_id)
    pv, erreur = _extraire_et_sauvegarder_point_vente(request, instance=pv_existant)

    if erreur:
        return JsonResponse({"erreur": erreur}, status=400)

    return JsonResponse(
        {
            "status": "success",
            "id": pv.id,
            "message": "Le point de vente a été mis à jour avec succès."
        },
        status=200
    ) """