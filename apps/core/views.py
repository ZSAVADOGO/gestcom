from datetime import datetime
from django.db import transaction
from django.utils.text import slugify
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from apps.hippisme.models import Course
from apps.resultats.models  import Resultat
from .lonab_bf_crawler import parse_resultats_lonab


from apps.hippisme.models import Course, Reunion, Hippodrome  # <-- Ajoutez Reunion ici !

from .lonab_bf_crawler import run_lonab_collector

def sauvegarder_donnees_crawler(data_crawler: dict, course_instance: Course = None) -> tuple[Resultat, bool]:
    """
    Sauvegarde les données du crawler en base.
    Retourne un tuple: (instance_resultat, cree_ou_mis_a_jour_boolean)
    """
    if not data_crawler:
        raise ValueError("Les données du crawler sont vides.")

    print("les donnes sont : data_crawler ", data_crawler)

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

        # Traitement du champ non_partants_ordre (chîne ou liste)
        npo_raw = data_crawler.get("non_partants_ordre", "Aucun")
        npo_val = " - ".join(npo_raw) if isinstance(npo_raw, list) else npo_raw

        # Sauvegarde ou Mise à jour dans Resultat
        #statut_resultat = getattr(Resultat.Statut, "OFFICIEL", "OFFICIEL") if hasattr(Resultat, "Statut") else "OFFICIEL"
        
        date_publier = datetime.fromisoformat(date_dt_raw)
        
        resultat_obj, created = Resultat.objects.update_or_create(
            course=course_instance,
            defaults={
                "statut": Resultat.Statut.PROVISOIRE,      
                "arrivee": arrivee_ordonnee,
                "non_partants": data_crawler.get("non_partants", "00"),
                "non_partants_ordre": npo_val,
                "rapports": data_crawler.get("rapports", {}),
                "source": Resultat.TypeSource.SCRAPING,
                "date_publication": date_publier,
                "donnees_brutes": data_crawler,  # Contient uniquement des données sérialisables en JSON
            }
        )

        return resultat_obj, created

@require_POST
def actualiser_donnees_view(request):
    """
    Vue déclenchée via AJAX pour récupérer et actualiser les derniers résultats.
    """
    try:
        # 1. Lancement de la collecte complète via le collector
        collecte = run_lonab_collector(max_pdf_pages=2)
        data_crawler = collecte.get("resultat_direct")

        if not data_crawler or not data_crawler.get("arrivee"):
            return JsonResponse({
                "status": "warning",
                "title": "Aucune donnée",
                "message": "⚠️ Aucune donnée d'arrivée complète n'a été trouvée sur le site de la LONAB."
            }, status=200)

        # 2. Enregistrement ou Mise à jour en base de données
        resultat, created = sauvegarder_donnees_crawler(data_crawler)

        # 3. Message dynamique selon le résultat (Ajout vs Mise à jour)
        if created:
            title = "Nouveau résultat enregistré !"
            msg = f"✨ Les données pour {resultat.course.nom} ont été ajoutées avec succès."
        else:
            title = "Résultat actualisé !"
            msg = f"🔄 Les données pour {resultat.course.nom} ont été mises à jour."

        return JsonResponse({
            "status": "success",
            "title": title,
            "message": msg
        }, status=200)

    except Exception as e:
        return JsonResponse({
            "status": "error",
            "title": "Erreur d'actualisation",
            "message": f"❌ Une erreur s'est produite : {str(e)}"
        }, status=500)

