from datetime import datetime, time
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils.dateparse import parse_date
from .models import Resultat

def lister_resultats(recherche="", statut="", date_debut=None, date_fin=None, page=1, page_size=12):
    """
    Service de filtrage et pagination pour les résultats de course.
    """
    queryset = Resultat.objects.select_related("course").all()

    # 1. Recherche textuelle libre
    if recherche:
        queryset = queryset.filter(
            Q(course__nom__icontains=recherche) |
            Q(course__code__icontains=recherche) |
            Q(commentaire__icontains=recherche) |
            Q(source__icontains=recherche) |
            Q(non_partants__icontains=recherche)
        )

    # 2. Filtre par Statut
    if statut:
        queryset = queryset.filter(statut=statut.upper())

    # 3. Filtres par Date
    if date_debut:
        if isinstance(date_debut, str):
            date_debut = parse_date(date_debut)
        if date_debut:
            queryset = queryset.filter(date_publication__gte=datetime.combine(date_debut, time.min))

    if date_fin:
        if isinstance(date_fin, str):
            date_fin = parse_date(date_fin)
        if date_fin:
            queryset = queryset.filter(date_publication__lte=datetime.combine(date_fin, time.max))

    queryset = queryset.order_by("-date_publication", "-id")

    page_size = max(1, page_size)
    paginator = Paginator(queryset, page_size)
    page_obj = paginator.get_page(page)

    # Sérialisation des objets
    objects_data = []
    for r in page_obj:
        brutes = getattr(r, "donnee_brutes", {}) or {}
        if not isinstance(brutes, dict):
            brutes = {}

        date_course = brutes.get("date_dt") or (
            r.date_publication.isoformat() if r.date_publication else ""
        )
        type_pari = brutes.get("titre") or (
            getattr(r.course, "type_pari", "Quarté") if r.course else "Quarté"
        )
        arrivee = r.arrivee or brutes.get("arrivee", [])
        non_partants = r.non_partants or brutes.get("non_partants", "00")
        non_partants_ordre = r.non_partants_ordre or " - ".join(brutes.get("non_partants_ordre", [])) or "Aucun"
        rapports = r.rapports or brutes.get("rapports", {})

        objects_data.append({
            "id": r.id,
            "course_id": r.course.id if r.course else None,
            "course_nom": str(r.course) if r.course else "Course N/A",
            "type_pari": type_pari,
            "date_course": date_course,
            "statut": r.statut,
            "statut_label": r.get_statut_display(),
            "arrivee": arrivee,
            "non_partants": non_partants,
            "non_partants_ordre": non_partants_ordre,
            "rapports": rapports,
            "temps_course": r.temps_course,
            "commentaire": r.commentaire,
            "source": r.source,
            "est_officiel": r.est_officiel,
            "date_publication": r.date_publication.strftime("%d/%m/%Y %H:%M") if r.date_publication else "",
            "date_officialisation": r.date_officialisation.strftime("%d/%m/%Y %H:%M") if r.date_officialisation else "",
        })

    pagination = {
        "page_courante": page_obj.number,
        "total_pages": paginator.num_pages,
        "total_elements": paginator.count,
        "taille_page": page_size,
        "a_precedent": page_obj.has_previous(),
        "a_suivant": page_obj.has_next(),
    }
    #print("return de lister_resultats ",objects_data)
    return {
        "status": "success",
        "objects": objects_data,
        "pagination": pagination,
        "resultats": objects_data,
    }
    
""" def lister_resultats(recherche="", statut="", date_debut=None, date_fin=None, page=1, page_size=12):
    #Service de filtrage et pagination pour les résultats de course.
    queryset = Resultat.objects.select_related("course").all()

    # 1. Recherche textuelle libre (course, commentaires, source, non-partants)
    if recherche:
        queryset = queryset.filter(
            Q(course__nom__icontains=recherche) |
            Q(course__code__icontains=recherche) |
            Q(commentaire__icontains=recherche) |
            Q(source__icontains=recherche) |
            Q(non_partants__icontains=recherche)
        )

    # 2. Filtre par Statut
    if statut:
        queryset = queryset.filter(statut=statut.upper())

    # 3. Filtres par Date
    if date_debut:
        if isinstance(date_debut, str):
            date_debut = parse_date(date_debut)
        if date_debut:
            queryset = queryset.filter(date_publication__gte=datetime.combine(date_debut, time.min))

    if date_fin:
        if isinstance(date_fin, str):
            date_fin = parse_date(date_fin)
        if date_fin:
            queryset = queryset.filter(date_publication__lte=datetime.combine(date_fin, time.max))

    queryset = queryset.order_by("-date_publication", "-id")

    page_size = max(1, page_size)
    paginator = Paginator(queryset, page_size)
    page_obj = paginator.get_page(page)

    # Sérialisation des objets pour l'API JSON et l'injection HTML
    objects_data = [
        {
            "id": r.id,
            "course_id": r.course.id if r.course else None,
            "course_nom": str(r.course) if r.course else "Course N/A",
            "statut": r.statut,
            "statut_label": r.get_statut_display(),
            "arrivee": r.arrivee,
            "non_partants": r.non_partants,
            "rapports": r.rapports,
            "temps_course": r.temps_course,
            "commentaire": r.commentaire,
            "source": r.source,
            "est_officiel": r.est_officiel,
            "date_publication": r.date_publication.strftime("%d/%m/%Y %H:%M") if r.date_publication else "",
            "date_officialisation": r.date_officialisation.strftime("%d/%m/%Y %H:%M") if r.date_officialisation else "",
        }
        for r in page_obj
    ]

    pagination = {
        "page_courante": page_obj.number,
        "total_pages": paginator.num_pages,
        "total_elements": paginator.count,
        "taille_page": page_size,
        "a_precedent": page_obj.has_previous(),
        "a_suivant": page_obj.has_next(),
    }

    return {
        "status": "success",
        "objects": objects_data,
        "pagination": pagination,
        "resultats": objects_data,  # Rétrocompatibilité
    } """