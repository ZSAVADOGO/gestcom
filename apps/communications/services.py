from django.core.paginator import Paginator
from django.db.models import Q
from .models import Communique

from django.utils.dateparse import parse_date
from datetime import datetime, time


""" def lister_communiques(recherche="", type_communique="", page=1, page_size=12):

    queryset = Communique.objects.all().order_by(
        "-est_a_la_une",
        "-ordre_affichage",
        "-date_publication"
    ) # On récupère tout (BROUILLON, PUBLIE, etc.)

    if recherche:
        queryset = queryset.filter(
            Q(titre__icontains=recherche)
            | Q(resume__icontains=recherche)
            | Q(contenu__icontains=recherche)
        )

    if type_communique:
        queryset = queryset.filter(type=type_communique) """
        
def lister_communiques(recherche="", type_communique="", statut="", date_debut=None, date_fin=None, page=1, page_size=12):
    """
    Fonction de filtre globale du QuerySet pour les communiqués.
    """
    queryset = Communique.objects.all()

    # 1. Recherche textuelle libre
    if recherche:
        queryset = queryset.filter(
            Q(titre__icontains=recherche) | 
            Q(resume__icontains=recherche) | 
            Q(contenu__icontains=recherche)
        )

    # 2. Filtre par Type (En majuscules pour correspondre aux TextChoices)
    if type_communique:
        queryset = queryset.filter(type=type_communique.upper())

    # 3. Filtre par Statut
    if statut:
        queryset = queryset.filter(statut=statut.upper())

    # 4. Filtre par Date de début (Début de journée 00:00:00)
    if date_debut:
        if isinstance(date_debut, str):
            date_debut = parse_date(date_debut)
        if date_debut:
            queryset = queryset.filter(date_publication__gte=datetime.combine(date_debut, time.min))

    # 5. Filtre par Date de fin (Fin de journée 23:59:59)
    if date_fin:
        if isinstance(date_fin, str):
            date_fin = parse_date(date_fin)
        if date_fin:
            queryset = queryset.filter(date_publication__lte=datetime.combine(date_fin, time.max))

    queryset = queryset.order_by("-id")
    
    # Sécurité pour éviter les tailles de page négatives ou nulles
    page_size = max(1, page_size)
    paginator = Paginator(queryset, page_size)
    page_obj = paginator.get_page(page)

    # Sérialisation simplifiée pour l'API JSON
    resultats = [
        {
            "id": c.id,
            "titre": c.titre,
            "resume": c.resume,
            "type": c.get_type_display(),
            "est_a_la_une": c.est_a_la_une,
            "date_publication": c.date_publication.strftime("%d/%m/%Y") if c.date_publication else None,
            # Ajoutez ici les autres champs nécessaires pour le rendu frontend
        }
        for c in page_obj
    ]

    pagination = {
        "page": page_obj.number,
        "total_pages": paginator.num_pages,
        "total_elements": paginator.count,
        "has_next": page_obj.has_next(),
        "has_previous": page_obj.has_previous(),
        "page_size": page_size,
    }

    return {
        "resultats": resultats,
        "pagination": pagination,
        # On peut aussi retourner le queryset original si le template Django en a besoin au chargement
        "objects": page_obj.object_list,
    }