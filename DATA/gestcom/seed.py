import os
import sys
import django
from decimal import Decimal
from datetime import date, timedelta, time

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.db import transaction
from django.utils import timezone

from apps.hippisme.models import Hippodrome, Entraineur, Jockey, Cheval, Reunion, Course, Partant
from apps.resultats.models import Resultat
from apps.points_vente.models import PointVente
from apps.communications.models import Communique
from apps.paris.models import Pari


def afficher(message):
    print(f"✓ {message}")


def creer_ou_mettre_a_jour(model, defaults=None, **kwargs):
    return model.objects.update_or_create(defaults=defaults or {}, **kwargs)


@transaction.atomic
def seed():
    print("\n" + "=" * 80)
    print(" SEED PMU - COURSES FRANCE (DEAUVILLE...) / CONTEXTE BURKINA FASO (FCFA)")
    print("=" * 80 + "\n")

    maintenant = timezone.now()
    aujourd_hui = timezone.localdate()
    hier = aujourd_hui - timedelta(days=1)
    demain = aujourd_hui + timedelta(days=1)

    # ========================================================
    # 1. HIPPODROMES FRANÇAIS (INCLUANT DEAUVILLE)
    # ========================================================
    hippodromes_data = [
        ("HPDEAUVILLE", "Hippodrome de Deauville-La Touques", "Deauville", "45 Avenue Hosea Ballou, 14800 Deauville", "49.3556000", "0.0742000", "Piste en gazon et PSF pour courses de plat."),
        ("HPAUTEUIL", "Hippodrome d'Auteuil", "Paris", "Bois de Boulogne, 75016 Paris", "48.8488000", "2.2517000", "Temple de l'obstacle en France."),
        ("HPVINCENNES", "Hippodrome Paris-Vincennes", "Paris", "2 Route de la Ferme, 75012 Paris", "48.8215000", "2.4558000", "La grande piste du trot mondial."),
        ("HPLYONPARILLY", "Hippodrome de Lyon-Parilly", "Lyon", "4 Avenue Pierre Mendès France, 69500 Bron", "45.7309000", "4.9169000", "Hippodrome pluridisciplinaire."),
    ]
    hippodromes = {}
    for code, nom, ville, adresse, lat, lon, desc in hippodromes_data:
        obj, _ = creer_ou_mettre_a_jour(
            Hippodrome, code=code,
            defaults={
                "nom": nom, "ville": ville, "pays": "France", "adresse": adresse,
                "latitude": Decimal(lat), "longitude": Decimal(lon),
                "description": desc, "est_actif": True
            }
        )
        hippodromes[code] = obj
    afficher(f"{len(hippodromes)} hippodromes français créés / mis à jour (dont Deauville)")

    # ========================================================
    # 2. ENTRAÎNEURS
    # ========================================================
    entraineurs_data = [
        "Jean-Claude Rouget", "André Fabre", "Francis-Henri Graffard", "Stéphane C think",
        "Thierry Duvaldestin", "François Nicolle", "Guillaume Macaire", "Philippe Allaire"
    ]
    entraineurs = []
    for i, nom in enumerate(entraineurs_data, 1):
        obj, _ = creer_ou_mettre_a_jour(
            Entraineur, code=f"ENT{i:03d}",
            defaults={
                "nom_complet": nom, "pays": "France",
                "telephone": f"+33 6 10 20 {i:02d} 01",
                "email": f"entraineur.{i}@pmu-turf.fr",
                "date_naissance": date(1965 + i, (i % 12) + 1, (i % 25) + 1),
                "est_actif": True
            }
        )
        entraineurs.append(obj)
    afficher(f"{len(entraineurs)} entraîneurs créés")

    # ========================================================
    # 3. JOCKEYS / DRIVERS
    # ========================================================
    jockeys_data = [
        "Christophe Soumillon", "Mickaël Barzalona", "Maxime Guyon", "Franck Nivard",
        "Éric Raffin", "Mathieu Abrivard", "James Reveley", "Angelo Zuliani",
        "Alexis Pouchin", "Théo Bachelot", "Yoann Lebourgeois", "Benjamin Rochard"
    ]
    jockeys = []
    for i, nom in enumerate(jockeys_data, 1):
        obj, _ = creer_ou_mettre_a_jour(
            Jockey, code=f"JOC{i:03d}",
            defaults={
                "nom_complet": nom, "pays": "France",
                "date_naissance": date(1985 + (i % 12), (i % 12) + 1, (i % 25) + 1),
                "poids_reference_kg": Decimal(str(52.0 + (i % 6) * 0.5)),
                "est_actif": True
            }
        )
        jockeys.append(obj)
    afficher(f"{len(jockeys)} jockeys / drivers créés")

    # ========================================================
    # 4. CHEVAUX
    # ========================================================
    chevaux_data = [
        ("CHE001", "Ace Impact", "MALE", "2020-02-15", "Alezan"),
        ("CHE002", "Iresine", "HONGRE", "2017-04-20", "Alezan"),
        ("CHE003", "Idao de Tillard", "MALE", "2018-03-12", "Baie"),
        ("CHE004", "Etonnant", "MALE", "2014-05-05", "Noir"),
        ("CHE005", "Gran Diose", "HONGRE", "2016-11-18", "Baie"),
        ("CHE006", "Jus de Citron", "MALE", "2019-05-07", "Gris"),
        ("CHE007", "Deauville Star", "FEMELLE", "2021-01-29", "Alezan"),
        ("CHE008", "Fleur du Kadiogo", "FEMELLE", "2021-08-11", "Baie"),
        ("CHE009", "Eclair de Liptako", "MALE", "2019-04-17", "Gris"),
        ("CHE010", "Princesse du Faso", "FEMELLE", "2020-12-02", "Alezan"),
        ("CHE011", "Vitesse Royale", "MALE", "2018-06-23", "Baie"),
        ("CHE012", "Le Phénix", "MALE", "2019-10-30", "Noir"),
        ("CHE013", "Duc de Normandie", "MALE", "2020-04-08", "Alezan"),
        ("CHE014", "Perle Noire", "FEMELLE", "2021-06-14", "Baie"),
        ("CHE015", "Major de la Côte", "MALE", "2019-02-20", "Gris"),
        ("CHE016", "Belle Touques", "FEMELLE", "2020-09-09", "Alezan"),
    ]
    chevaux = []
    for i, (code, nom, sexe, naissance, couleur) in enumerate(chevaux_data):
        obj, _ = creer_ou_mettre_a_jour(
            Cheval, numero_enregistrement=code,
            defaults={
                "nom": nom, "sexe": sexe, "date_naissance": date.fromisoformat(naissance),
                "race": "Pur-sang" if i % 2 == 0 else "Trotteur Français", "couleur": couleur,
                "proprietaire": f"Écurie France-Gagnant {(i % 3) + 1}",
                "entraineur_actuel": entraineurs[i % len(entraineurs)], "est_actif": True
            }
        )
        chevaux.append(obj)
    afficher(f"{len(chevaux)} chevaux créés")

    # ========================================================
    # 5. RÉUNIONS (INCLUANT DEAUVILLE)
    # ========================================================
    reunion_specs = [
        ("R1", hier, "R1 - Deauville", "HPDEAUVILLE", 1, time(13, 50), "TERMINEE", 8, 8),
        ("R2", aujourd_hui, "R2 - Paris-Vincennes", "HPVINCENNES", 2, time(11, 30), "PROGRAMMEE", 8, 0),
        ("R3", demain, "R3 - Auteuil", "HPAUTEUIL", 3, time(16, 0), "PROGRAMMEE", 8, 0),
    ]
    reunions = {}
    for code_prefix, jour, nom, hp_code, numero, heure, statut, nb_prevu, nb_terminees in reunion_specs:
        obj, _ = creer_ou_mettre_a_jour(
            Reunion, code=f"{code_prefix}-{jour.strftime('%Y%m%d')}",
            defaults={
                "numero": numero, "nom": nom, "hippodrome": hippodromes[hp_code],
                "date_reunion": jour, "heure_debut": heure, "statut": statut,
                "nombre_courses_prevu": nb_prevu, "nombre_courses_terminees": nb_terminees,
                "description": "Réunion hippique officielle. Support des paris PMU."
            }
        )
        reunions[code_prefix] = obj
    afficher("3 réunions créées (Deauville, Vincennes, Auteuil)")

    # ========================================================
    # 6. COURSES
    # ========================================================
    programmes = {
        "R1": [
            (1, "GRAND HANDICAP DE DEAUVILLE", "PLAT", 1600, "13:50"),
            (2, "PRIX DE LA CÔTE DE GRÂCE", "PLAT", 1200, "14:25"),
            (3, "PRIX GUILLAUME D'ORNANO", "PLAT", 2000, "15:00"),
            (4, "PRIX DE DUBAI DUTY FREE", "PLAT", 1400, "15:35"),
            (5, "PRIX DU CALVADOS", "PLAT", 1400, "16:10"),
            (6, "PRIX DE LA HARAS DE FRESNAY", "PLAT", 1600, "16:45"),
            (7, "PRIX DES MARETTES", "PLAT", 1500, "17:20"),
            (8, "PRIX DE THOURIE", "PLAT", 1900, "17:55"),
        ],
        "R2": [
            (1, "PRIX DE FRANCE", "ATTELE", 2100, "11:30"),
            (2, "PRIX DE PARIS", "ATTELE", 4150, "12:05"),
            (3, "PRIX DE CENTAURE", "MONTE", 2175, "12:40"),
            (4, "PRIX DE SEUTRÉ", "ATTELE", 2700, "13:15"),
            (5, "PRIX DE LOUVROIL", "ATTELE", 2850, "13:50"),
            (6, "PRIX DU LUXEMBOURG", "ATTELE", 2100, "14:25"),
            (7, "PRIX DE ROISSY", "ATTELE", 2700, "15:00"),
            (8, "PRIX DE CAMBRESIS", "ATTELE", 2850, "15:35"),
        ],
        "R3": [
            (1, "PRIX LE PARISIEN (GRAND STEEPLE)", "OBSTACLE", 4400, "16:00"),
            (2, "PRIX CAMBACÉRÈS", "OBSTACLE", 3600, "16:35"),
            (3, "PRIX MAURICE GILLOIS", "OBSTACLE", 4400, "17:10"),
            (4, "PRIX LA HAYE JOUSSELIN", "OBSTACLE", 5500, "17:45"),
            (5, "PRIX HERON", "OBSTACLE", 3500, "18:20"),
            (6, "PRIX CARMARTHEN", "OBSTACLE", 3900, "18:55"),
            (7, "PRIX JEAN STERN", "OBSTACLE", 4400, "19:30"),
            (8, "PRIX COREANA", "OBSTACLE", 3600, "20:05"),
        ],
    }

    courses = []
    for reunion_code, programme in programmes.items():
        reunion = reunions[reunion_code]
        for numero, nom, categorie, distance, heure_str in programme:
            support = (reunion_code == "R1" and numero == 1) or (reunion_code == "R2" and numero == 4)
            course, _ = creer_ou_mettre_a_jour(
                Course,
                code=f"{reunion_code}C{numero}-{reunion.date_reunion.strftime('%Y%m%d')}",
                defaults={
                    "reunion": reunion,
                    "numero": numero,
                    "nom": nom + (" - QUINTÉ+" if support else ""),
                    "categorie": categorie,
                    "distance_metres": distance,
                    "nombre_partants_prevu": 16,
                    "heure_depart": time.fromisoformat(heure_str),
                    "statut": "TERMINEE" if reunion_code == "R1" else "PROGRAMMEE",
                    "est_active": True,
                    "allocation": Decimal("100000.00" if support else "48000.00"),
                    "conditions": "Course événement nationale - Support Quinté+ PMU." if support else "Course officielle hors événement.",
                },
            )
            courses.append(course)
    afficher(f"{len(courses)} courses créées")

    # ========================================================
    # 7. PARTANTS
    # ========================================================
    partants_par_course = {}
    for ci, course in enumerate(courses):
        partants = []
        for numero in range(1, 17):
            cheval = chevaux[(ci * 3 + numero - 1) % len(chevaux)]
            jockey = jockeys[(ci + numero - 1) % len(jockeys)]
            non_partant = course.reunion.numero == 2 and course.numero == 8 and numero in (5, 12)
            obj, _ = creer_ou_mettre_a_jour(
                Partant, course=course, numero=numero,
                defaults={
                    "cheval": cheval,
                    "jockey": jockey,
                    "entraineur": cheval.entraineur_actuel,
                    "corde": numero if course.categorie == "PLAT" else None,
                    "poids_kg": Decimal(str(53 + (numero % 7) * 0.5)),
                    "age": aujourd_hui.year - cheval.date_naissance.year,
                    "cote": Decimal(str(round(2.8 + numero * 1.2, 2))),
                    "est_non_partant": non_partant,
                    "raison_non_partant": "Forfait vétérinaire" if non_partant else "",
                    "observations": "Régulier dans la catégorie.",
                    "donnees_source": {"source": "OFFICIEL_PMU", "statut": "NON_PARTANT" if non_partant else "PARTANT"},
                },
            )
            partants.append(obj)
        partants_par_course[course.pk] = partants
    afficher(f"{Partant.objects.count()} partants synchronisés")

    # ========================================================
    # 8. RÉSULTATS ET RAPPORTS (CONTEXTE DEAUVILLE EN FCFA)
    # ========================================================
    r1_courses = [c for c in courses if c.reunion_id == reunions["R1"].id]
    for ci, course in enumerate(r1_courses):
        partants = partants_par_course[course.pk]
        candidats = [((ci * 3 + 7) % 16) + 1, ((ci * 5 + 3) % 16) + 1, ((ci * 7 + 1) % 16) + 1,
                     ((ci * 2 + 10) % 16) + 1, ((ci * 4 + 5) % 16) + 1]
        numeros = list(dict.fromkeys(candidats))
        arrivee = []
        for position, numero in enumerate(numeros, 1):
            partant = next((p for p in partants if p.numero == numero and not p.est_non_partant), None)
            if partant:
                arrivee.append({
                    "position": position,
                    "numero": numero,
                    "cheval": partant.cheval.nom,
                    "jockey": partant.jockey.nom_complet if partant.jockey else None,
                })
        creer_ou_mettre_a_jour(
            Resultat, course=course,
            defaults={
                "statut": "OFFICIEL",
                "arrivee": arrivee,
                "rapports": {
                    "simple_gagnant": {"numero": arrivee[0]["numero"], "rapport": round(1500 + ci * 250, 0)},
                    "couple": {"combinaison": f"{arrivee[0]['numero']}-{arrivee[1]['numero']}", "rapport": round(6500 + ci * 1200, 0)},
                    "tierce": {"ordre": 450000 + ci * 25000, "desordre": 85000 + ci * 5000},
                    "quarte": {"ordre": 1850000 + ci * 150000, "desordre": 240000 + ci * 15000},
                    "quinte": {"ordre": 12500000 + ci * 500000, "desordre": 850000 + ci * 40000},
                },
                "temps_course": f"01:{38 + ci:02d}:45",
                "commentaire": "Arrivée officielle validée par les commissaires.",
                "date_publication": maintenant,
                "date_officialisation": maintenant,
                "source": "LONGBOW_PMU_BURKINA",
                "donnees_brutes": {"source_type": "OFFICIELLE", "reunion": "R1", "course": f"C{course.numero}"},
            },
        )
    afficher(f"{Resultat.objects.count()} résultat(s) validé(s)")

    # ========================================================
    # 9. POINTS DE VENTE - BURKINA FASO (RÉSEAU LONAB / PMU-B)
    # ========================================================
    points_data = [
        ("PV001", "Agence Principale PMU - Kwame N'Krumah", "Ouagadougou", "Koulouba", "Avenue Kwame N'Krumah, face à la BCAO", "+226 25 30 60 01", "12.3715000", "-1.5199000", "AGENCE"),
        ("PV002", "Point de Vente PMU - Tampouy", "Ouagadougou", "Tampouy", "Boulevard Paul VI, près de l'échangeur du Nord", "+226 70 21 00 02", "12.3891000", "-1.5481000", "POINT_VENTE"),
        ("PV003", "Point de Vente PMU - Ouaga 2000", "Ouagadougou", "Ouaga 2000", "Avenue Pascal Zagré, à côté de la Pharmacie", "+226 70 21 00 03", "12.3345000", "-1.4936000", "POINT_VENTE"),
        ("PV004", "Point de Vente PMU - Patte d'Oie", "Ouagadougou", "Patte d'Oie", "Près de la Gare Routière Ouaga-Inter", "+226 70 21 00 04", "12.3412000", "-1.5123000", "POINT_VENTE"),
        ("PV005", "Agence Régionale PMU - Bobo Centre", "Bobo-Dioulasso", "Commercial", "Avenue de la République, près de la BIAO", "+226 20 97 10 05", "11.1770000", "-4.2977000", "AGENCE"),
        ("PV006", "Point de Vente PMU - Koudougou Centre", "Koudougou", "Sector 1", "Marché Central, Rue du Commerce", "+226 25 44 00 06", "12.2510000", "-2.3610000", "POINT_VENTE"),
    ]
    points_vente = []
    for code, nom, ville, quartier, adresse, telephone, lat, lon, type_point in points_data:
        obj, _ = creer_ou_mettre_a_jour(
            PointVente, code=code,
            defaults={
                "nom": nom, "type": type_point, "ville": ville, "quartier": quartier, "adresse": adresse,
                "telephone": telephone, "latitude": Decimal(lat), "longitude": Decimal(lon),
                "description": "Point de vente agréé PMU Burkina Faso.",
                "est_actif": True, "est_principal": code in ("PV001", "PV005"),
                "horaires": {
                    "lundi": "07:30-18:30", "mardi": "07:30-18:30", "mercredi": "07:30-18:30",
                    "jeudi": "07:30-18:30", "vendredi": "07:30-18:30", "samedi": "07:30-18:30", "dimanche": "08:00-16:00"
                },
                "services": ["Prise de paris en direct", "Paiement immédiat des gains", "Vérification automatique des tickets", "Consultation du Programme"],
            },
        )
        points_vente.append(obj)
    afficher(f"{len(points_vente)} points de vente burkinabè configurés")

    # ========================================================
    # 10. COMMUNICATIONS / COMMUNIQUÉS (CONTEXTE PMU BURKINA)
    # ========================================================
    communiques = [
        (
            "Programme Quinté+ du Jour - Deauville",
            "Consultez les 16 partants du Grand Handicap de Deauville et faites vos jeux dans vos agences.",
            "PROGRAMME", True,
            "<p><strong>Avis aux parieurs :</strong> Le Quinté+ du jour se court sur l'hippodrome de Deauville-La Touques. Départ prévu à 13h50. Retrouvez les cotes actualisées et les avis des experts dans tous les points de vente agréés.</p>"
        ),
        (
            "Mise en garde contre les fraudes et faux tickets",
            "Exigez toujours un reçu imprimé depuis un terminal officiel lors de la prise de votre pari.",
            "ALERTE", True,
            "<p>La Direction Générale rappelle aux parieurs que seuls les tickets émis par les terminaux autorisés font foi. N'achetez aucun ticket en dehors des guichets agréés sous peine de nullité.</p>"
        ),
        (
            "Extinction progressive des délais de paiement des gains",
            "Les gains s'élevant jusqu'à 500 000 FCFA sont désormais payables immédiatement au guichet.",
            "ANNONCE", False,
            "<p>Pour simplifier les démarches de nos heureux gagnants, les paiements jusqu'à 500 000 FCFA s'effectuent cash sur présentation du ticket original valide dans n'importe quelle agence régionale.</p>"
        ),
    ]
    for i, (titre, resume, type_communique, une, contenu) in enumerate(communiques, 1):
        creer_ou_mettre_a_jour(
            Communique, titre=titre,
            defaults={
                "resume": resume, "contenu": contenu, "type": type_communique, "statut": "PUBLIE",
                "date_publication": maintenant - timedelta(hours=i), "est_a_la_une": une,
                "ordre_affichage": i, "nombre_vues": 120 * i,
                "metadonnees": {"source": "COMMUNICATION_OFFICIELLE", "pays": "Burkina Faso", "devise": "XOF"}
            },
        )
    afficher(f"{len(communiques)} communiqués enregistrés")

    # ========================================================
    # 11. TICKETS / PARIS (MONTANTS EN FCFA)
    # ========================================================
    course_support = next(c for c in courses if c.reunion_id == reunions["R1"].id and c.numero == 1)
    tickets = [
        ("TKT-BF-2026-0001", "SIMPLE", "500.00", "3500.00", "GAGNANT", [{"numero": 8, "position": 1}]),
        ("TKT-BF-2026-0002", "COUPLE", "1000.00", "12500.00", "GAGNANT", [{"numero": 8, "position": 1}, {"numero": 4, "position": 2}]),
        ("TKT-BF-2026-0003", "TIERCE", "1000.00", "480000.00", "GAGNANT", [{"numero": 8, "position": 1}, {"numero": 4, "position": 2}, {"numero": 12, "position": 3}]),
        ("TKT-BF-2026-0004", "QUARTE", "1500.00", "0.00", "PERDANT", [{"numero": 1, "position": 1}, {"numero": 3, "position": 2}, {"numero": 5, "position": 3}, {"numero": 7, "position": 4}]),
        ("TKT-BF-2026-0005", "QUINTE", "2000.00", "13000000.00", "GAGNANT", [{"numero": 8, "position": 1}, {"numero": 4, "position": 2}, {"numero": 12, "position": 3}, {"numero": 6, "position": 4}, {"numero": 15, "position": 5}]),
        ("TKT-BF-2026-0006", "TIERCE", "1000.00", "0.00", "EN_ATTENTE", [{"numero": 3, "position": 1}, {"numero": 6, "position": 2}, {"numero": 10, "position": 3}]),
    ]
    for numero_ticket, type_pari, mise, gain, statut, selections in tickets:
        verifie = statut in ("GAGNANT", "PERDANT")
        creer_ou_mettre_a_jour(
            Pari, numero_ticket=numero_ticket,
            defaults={
                "type": type_pari, "course": course_support, "point_vente": points_vente[0],
                "montant_mise": Decimal(mise), "montant_gain": Decimal(gain), "selections": selections,
                "statut": statut, "est_verifie": verifie,
                "date_prise": maintenant - timedelta(hours=3),
                "date_verification": maintenant if verifie else None,
                "date_paiement": maintenant if statut == "GAGNANT" else None,
                "reference_externe": f"REF-BF-{numero_ticket}",
                "donnees_ticket": {
                    "canal": "TERMINAL_POINT_VENTE",
                    "terminal_id": "TMR-OUAGA-0102",
                    "devise": "XOF",
                    "agence": points_vente[0].nom
                },
            },
        )
    afficher(f"{len(tickets)} tickets de jeu générés")

    # ========================================================
    # 12. RÉCAPITULATIF
    # ========================================================
    print("\n" + "=" * 80)
    print(" EXÉCUTION DU SEED AVEC SUCCÈS")
    print("=" * 80)
    print(f" • Hippodromes (France)  : {Hippodrome.objects.count()}")
    print(f" • Entraîneurs           : {Entraineur.objects.count()}")
    print(f" • Jockeys               : {Jockey.objects.count()}")
    print(f" • Chevaux               : {Cheval.objects.count()}")
    print(f" • Réunions              : {Reunion.objects.count()}")
    print(f" • Courses               : {Course.objects.count()}")
    print(f" • Partants              : {Partant.objects.count()}")
    print(f" • Résultats             : {Resultat.objects.count()}")
    print(f" • Points de Vente (BF)  : {PointVente.objects.count()}")
    print(f" • Communiqués           : {Communique.objects.count()}")
    print(f" • Paris / Tickets       : {Pari.objects.count()}")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    seed()