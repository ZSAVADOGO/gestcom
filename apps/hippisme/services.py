from django.db import transaction
from django.db.models import Q, Count, Prefetch
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import (
    Hippodrome,
    Entraineur,
    Jockey,
    Cheval,
    Reunion,
    Course,
    Partant,
)


class HippismeService:
    """
    Service métier central de l'application hippisme.

    Les vues ne doivent pas contenir la logique métier complexe.
    Elles délèguent les opérations à cette classe.
    """

    # =========================================================
    # TABLEAU DE BORD
    # =========================================================

    @staticmethod
    def statistiques():
        aujourd_hui = timezone.localdate()

        return {
            "nombre_hippodromes": Hippodrome.objects.filter(
                est_actif=True
            ).count(),

            "nombre_entraineurs": Entraineur.objects.filter(
                est_actif=True
            ).count(),

            "nombre_jockeys": Jockey.objects.filter(
                est_actif=True
            ).count(),

            "nombre_chevaux": Cheval.objects.filter(
                est_actif=True
            ).count(),

            "nombre_reunions": Reunion.objects.filter(
                date_reunion=aujourd_hui
            ).count(),

            "nombre_courses": Course.objects.filter(
                reunion__date_reunion=aujourd_hui,
                est_active=True
            ).count(),

            "nombre_partants": Partant.objects.filter(
                course__reunion__date_reunion=aujourd_hui,
                est_non_partant=False
            ).count(),
        }

    # =========================================================
    # HIPPODROMES
    # =========================================================

    @staticmethod
    def liste_hippodromes(recherche=None, ville=None, actifs_seulement=True):
        queryset = Hippodrome.objects.all()

        if actifs_seulement:
            queryset = queryset.filter(est_actif=True)

        if recherche:
            queryset = queryset.filter(
                Q(nom__icontains=recherche)
                | Q(code__icontains=recherche)
                | Q(ville__icontains=recherche)
                | Q(pays__icontains=recherche)
            )

        if ville:
            queryset = queryset.filter(ville__icontains=ville)

        return queryset.order_by("nom")

    @staticmethod
    def obtenir_hippodrome(pk):
        return get_object_or_404(Hippodrome, pk=pk)

    @staticmethod
    @transaction.atomic
    def creer_hippodrome(donnees):
        return Hippodrome.objects.create(**donnees)

    @staticmethod
    @transaction.atomic
    def modifier_hippodrome(hippodrome, donnees):
        for champ, valeur in donnees.items():
            setattr(hippodrome, champ, valeur)

        hippodrome.save()
        return hippodrome

    @staticmethod
    @transaction.atomic
    def supprimer_hippodrome(hippodrome):
        hippodrome.delete()

    # =========================================================
    # ENTRAÎNEURS
    # =========================================================

    @staticmethod
    def liste_entraineurs(recherche=None, actifs_seulement=True):
        queryset = Entraineur.objects.all()

        if actifs_seulement:
            queryset = queryset.filter(est_actif=True)

        if recherche:
            queryset = queryset.filter(
                Q(nom_complet__icontains=recherche)
                | Q(code__icontains=recherche)
                | Q(pays__icontains=recherche)
            )

        return queryset.order_by("nom_complet")

    @staticmethod
    def obtenir_entraineur(pk):
        return get_object_or_404(Entraineur, pk=pk)

    @staticmethod
    @transaction.atomic
    def creer_entraineur(donnees):
        return Entraineur.objects.create(**donnees)

    @staticmethod
    @transaction.atomic
    def modifier_entraineur(entraineur, donnees):
        for champ, valeur in donnees.items():
            setattr(entraineur, champ, valeur)

        entraineur.save()
        return entraineur

    @staticmethod
    @transaction.atomic
    def supprimer_entraineur(entraineur):
        entraineur.delete()

    # =========================================================
    # JOCKEYS
    # =========================================================

    @staticmethod
    def liste_jockeys(recherche=None, actifs_seulement=True):
        queryset = Jockey.objects.all()

        if actifs_seulement:
            queryset = queryset.filter(est_actif=True)

        if recherche:
            queryset = queryset.filter(
                Q(nom_complet__icontains=recherche)
                | Q(code__icontains=recherche)
                | Q(pays__icontains=recherche)
            )

        return queryset.order_by("nom_complet")

    @staticmethod
    def obtenir_jockey(pk):
        return get_object_or_404(Jockey, pk=pk)

    @staticmethod
    @transaction.atomic
    def creer_jockey(donnees):
        return Jockey.objects.create(**donnees)

    @staticmethod
    @transaction.atomic
    def modifier_jockey(jockey, donnees):
        for champ, valeur in donnees.items():
            setattr(jockey, champ, valeur)

        jockey.save()
        return jockey

    @staticmethod
    @transaction.atomic
    def supprimer_jockey(jockey):
        jockey.delete()

    # =========================================================
    # CHEVAUX
    # =========================================================

    @staticmethod
    def liste_chevaux(
        recherche=None,
        sexe=None,
        entraineur=None,
        actifs_seulement=True
    ):
        queryset = (
            Cheval.objects
            .select_related("entraineur_actuel")
            .all()
        )

        if actifs_seulement:
            queryset = queryset.filter(est_actif=True)

        if recherche:
            queryset = queryset.filter(
                Q(nom__icontains=recherche)
                | Q(numero_enregistrement__icontains=recherche)
                | Q(proprietaire__icontains=recherche)
            )

        if sexe:
            queryset = queryset.filter(sexe=sexe)

        if entraineur:
            queryset = queryset.filter(
                entraineur_actuel_id=entraineur
            )

        return queryset.order_by("nom")

    @staticmethod
    def obtenir_cheval(pk):
        return get_object_or_404(
            Cheval.objects.select_related("entraineur_actuel"),
            pk=pk
        )

    @staticmethod
    @transaction.atomic
    def creer_cheval(donnees):
        return Cheval.objects.create(**donnees)

    @staticmethod
    @transaction.atomic
    def modifier_cheval(cheval, donnees):
        for champ, valeur in donnees.items():
            setattr(cheval, champ, valeur)

        cheval.save()
        return cheval

    @staticmethod
    @transaction.atomic
    def supprimer_cheval(cheval):
        cheval.delete()

    # =========================================================
    # RÉUNIONS
    # =========================================================

    @staticmethod
    def liste_reunions(
        date_reunion=None,
        hippodrome=None,
        statut=None
    ):
        queryset = (
            Reunion.objects
            .select_related("hippodrome")
            .annotate(
                nombre_courses=Count("courses")
            )
            .all()
        )

        if date_reunion:
            queryset = queryset.filter(
                date_reunion=date_reunion
            )

        if hippodrome:
            queryset = queryset.filter(
                hippodrome_id=hippodrome
            )

        if statut:
            queryset = queryset.filter(
                statut=statut
            )

        return queryset.order_by(
            "-date_reunion",
            "numero"
        )

    @staticmethod
    def reunions_du_jour():
        return HippismeService.liste_reunions(
            date_reunion=timezone.localdate()
        )

    @staticmethod
    def obtenir_reunion(pk):
        return get_object_or_404(
            Reunion.objects.select_related("hippodrome"),
            pk=pk
        )

    @staticmethod
    @transaction.atomic
    def creer_reunion(donnees):
        return Reunion.objects.create(**donnees)

    @staticmethod
    @transaction.atomic
    def modifier_reunion(reunion, donnees):
        for champ, valeur in donnees.items():
            setattr(reunion, champ, valeur)

        reunion.save()
        return reunion

    @staticmethod
    @transaction.atomic
    def supprimer_reunion(reunion):
        reunion.delete()

    # =========================================================
    # COURSES
    # =========================================================

    @staticmethod
    def liste_courses(
        recherche=None,
        reunion=None,
        date_reunion=None,
        statut=None,
        categorie=None
    ):
        queryset = (
            Course.objects
            .select_related(
                "reunion",
                "reunion__hippodrome"
            )
            .all()
        )

        if recherche:
            queryset = queryset.filter(
                Q(nom__icontains=recherche)
                | Q(code__icontains=recherche)
            )

        if reunion:
            queryset = queryset.filter(
                reunion_id=reunion
            )

        if date_reunion:
            queryset = queryset.filter(
                reunion__date_reunion=date_reunion
            )

        if statut:
            queryset = queryset.filter(
                statut=statut
            )

        if categorie:
            queryset = queryset.filter(
                categorie=categorie
            )

        return queryset.order_by(
            "reunion__date_reunion",
            "numero"
        )

    @staticmethod
    def courses_du_jour():
        return HippismeService.liste_courses(
            date_reunion=timezone.localdate()
        )

    @staticmethod
    def obtenir_course(pk):
        return get_object_or_404(
            Course.objects.select_related(
                "reunion",
                "reunion__hippodrome"
            ),
            pk=pk
        )

    @staticmethod
    def obtenir_course_avec_partants(pk):
        return get_object_or_404(
            Course.objects
            .select_related(
                "reunion",
                "reunion__hippodrome"
            )
            .prefetch_related(
                Prefetch(
                    "partants",
                    queryset=Partant.objects.select_related(
                        "cheval",
                        "jockey",
                        "entraineur"
                    ).order_by("numero")
                )
            ),
            pk=pk
        )

    @staticmethod
    @transaction.atomic
    def creer_course(donnees):
        return Course.objects.create(**donnees)

    @staticmethod
    @transaction.atomic
    def modifier_course(course, donnees):
        for champ, valeur in donnees.items():
            setattr(course, champ, valeur)

        course.save()
        return course

    @staticmethod
    @transaction.atomic
    def supprimer_course(course):
        course.delete()

    # =========================================================
    # PARTANTS
    # =========================================================

    @staticmethod
    def liste_partants(
        course=None,
        cheval=None,
        jockey=None,
        entraineur=None,
        uniquement_partants=True
    ):
        queryset = (
            Partant.objects
            .select_related(
                "course",
                "cheval",
                "jockey",
                "entraineur",
                "course__reunion"
            )
            .all()
        )

        if course:
            queryset = queryset.filter(
                course_id=course
            )

        if cheval:
            queryset = queryset.filter(
                cheval_id=cheval
            )

        if jockey:
            queryset = queryset.filter(
                jockey_id=jockey
            )

        if entraineur:
            queryset = queryset.filter(
                entraineur_id=entraineur
            )

        if uniquement_partants:
            queryset = queryset.filter(
                est_non_partant=False
            )

        return queryset.order_by(
            "course__reunion__date_reunion",
            "course__numero",
            "numero"
        )

    @staticmethod
    def obtenir_partant(pk):
        return get_object_or_404(
            Partant.objects.select_related(
                "course",
                "cheval",
                "jockey",
                "entraineur",
                "course__reunion"
            ),
            pk=pk
        )

    @staticmethod
    @transaction.atomic
    def creer_partant(donnees):
        return Partant.objects.create(**donnees)

    @staticmethod
    @transaction.atomic
    def modifier_partant(partant, donnees):
        for champ, valeur in donnees.items():
            setattr(partant, champ, valeur)

        partant.save()
        return partant

    @staticmethod
    @transaction.atomic
    def supprimer_partant(partant):
        partant.delete()