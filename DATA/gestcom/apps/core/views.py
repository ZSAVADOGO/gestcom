from datetime import datetime
from django.db import transaction
from django.utils.text import slugify
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.shortcuts import redirect

from django.utils import timezone
from apps.hippisme.models import Course
from apps.resultats.models  import Resultat
from .lonab_bf_crawler import parse_resultats_lonab

from apps.hippisme.models import Course, Reunion, Hippodrome  # <-- Ajoutez Reunion ici !

from .lonab_bf_crawler import run_lonab_collector


def sauvegarder_donnees_crawler(data_crawler: dict, course_instance: Course = None) -> Resultat:
    if not data_crawler:
        raise ValueError("Les données du crawler sont vides.")

    with transaction.atomic():
        if course_instance is None:
            titre = data_crawler.get("titre", "Course PMU - LONAB")
            date_str = data_crawler.get("date_str", "")
            
            # Slug de date pour le code unique
            date_slug = slugify(date_str) if date_str else timezone.localdate().strftime("%Y-%m-%d")
            code_course = f"LONAB-{date_slug}"

            # Récupération de la date au format datetime si présente
            date_dt_raw = data_crawler.get("date_dt")
            if isinstance(date_dt_raw, str):
                try:
                    date_reunion = datetime.fromisoformat(date_dt_raw).date()
                except ValueError:
                    date_reunion = timezone.localdate()
            else:
                date_reunion = timezone.localdate()

            # Réunion par défaut
            reunion_defaut, _ = Reunion.objects.get_or_create(
                code=f"R1-LONAB-{date_slug}",
                defaults={
                    "nom": f"Réunion LONAB - {date_str}",
                    "date_reunion": date_reunion,
                    "numero": 1,
                    "statut": "TERMINEE",
                }
            )

            # Course par défaut
            course_instance, _ = Course.objects.get_or_create(
                code=code_course,
                defaults={
                    "nom": titre,
                    "reunion": reunion_defaut,
                    "numero": data_crawler.get("numero_course", 1),
                    "distance_metres": data_crawler.get("distance", 1600),
                    "statut": getattr(Course.Statut, "RESULTAT_OFFICIEL", "TERMINEE"),
                    "est_active": True,
                }
            )

        # Arrivée ordonnée pour JSONField
        arrivee_brute = data_crawler.get("arrivee", [])
        arrivee_ordonnee = [
            {"position": i, "numero": int(num) if str(num).isdigit() else num}
            for i, num in enumerate(arrivee_brute, start=1)
        ]

        # Sauvegarde dans Resultat
        statut_resultat = getattr(Resultat.Statut, "OFFICIEL", "OFFICIEL") if hasattr(Resultat, "Statut") else "OFFICIEL"

        resultat_obj, created = Resultat.objects.update_or_create(
            course=course_instance,
            defaults={
                "statut": statut_resultat,
                "arrivee": arrivee_ordonnee,
                "rapports": data_crawler.get("rapports", {}),
                "source": "LONAB Web Scraper",
                "date_publication": timezone.now(),
                "donnees_brutes": data_crawler,  # Contient uniquement des données sérialisables en JSON
            }
        )

        return resultat_obj


@require_POST
def actualiser_donnees_view(request):
    """
    Vue déclenchée par la Navbar pour récupérer les derniers résultats.
    """
    referer = request.META.get('HTTP_REFERER', '/')
    try:
        # 1. Lancement de la collecte complète via le collector
        collecte = run_lonab_collector(max_pdf_pages=2)
        data_crawler = collecte.get("resultat_direct")

        if not data_crawler or not data_crawler.get("arrivee"):
            messages.warning(request, "⚠️ Aucune donnée d'arrivée complète n'a été trouvée sur le site de la LONAB.")
            return redirect(referer)

        # 2. Enregistrement en base de données
        resultat = sauvegarder_donnees_crawler(data_crawler)

        # 3. Notification utilisateur
        messages.success(
            request, 
            f"🔄 Résultat officiel actualisé avec succès pour : {resultat.course.nom} !"
        )

    except Exception as e:
        messages.error(request, f"❌ Erreur lors de l'actualisation : {str(e)}")

    return redirect(referer)