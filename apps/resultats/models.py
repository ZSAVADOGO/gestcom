from django.db import models

from apps.core.models import ModeleAuditable
from apps.hippisme.models import Course
from datetime import datetime

from django.utils import timezone




class Resultat(ModeleAuditable):
    class Statut(models.TextChoices):
        PROVISOIRE = "PROVISOIRE", "Provisoire"
        OFFICIEL = "OFFICIEL", "Officiel"
        ANNULE = "ANNULE", "Annulé"
    
    # Ajout des types de sources sélectionnables
    class TypeSource(models.TextChoices):
        MANUEL = "MANUEL", "Manuel"
        AUTOMATIQUE = "AUTOMATIQUE", "Automatique"
        API = "API", "API Externe"
        SCRAPING = "SCRAPING_LONAB_BF", "Scraping le site WEB de la LONAB"

    """ course = models.OneToOneField(
            "Course",
            on_delete=models.CASCADE,
            related_name="resultat",
            verbose_name="Course"
        ) """
        
    course = models.OneToOneField(
        "hippisme.Course", # Ou 'Course' si dans la même app
        on_delete=models.CASCADE,
        related_name="resultat",
        null=True,  # <--- Permet de tester sans instance de Course
        blank=True
    )

    statut = models.CharField(
        max_length=20,
        choices=Statut.choices,
        default=Statut.PROVISOIRE,
        db_index=True
    )

    # Structure : [{"rang": 1, "cheval": "14"}, {"rang": 2, "cheval": "3"}, ...]
    arrivee = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Arrivée ordonnée",
        help_text="Liste d'objets structurés : [{'rang': 1, 'cheval': '14'}, ...]"
    )

    non_partants = models.CharField(
        max_length=50,
        default="00",
        blank=True,
        verbose_name="Non-partants (NP)"
    )
    
    non_partants_ordre = models.CharField(
        max_length=100,
        default="Aucun",
        blank=True,
        verbose_name="Non-partants d'ordre (NPO)"
    )

    # Structure : {"Ordre": 10264500, "Désordre": 25500, ...}
    rapports = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Rapports de gains"
    )

    temps_course = models.CharField(
        max_length=50,
        blank=True
    )

    commentaire = models.TextField(
        blank=True
    )

    date_publication = models.DateTimeField(
        default=timezone.now,
        null=True,
        blank=True,
        db_index=True
    )

    date_officialisation = models.DateTimeField(
        null=True,
        blank=True
    )

    # Champ source optimisé avec choix multiples et indexé
    source = models.CharField(
        max_length=20,
        choices=TypeSource.choices,
        default=TypeSource.MANUEL,
        db_index=True,
        verbose_name="Source des données"
    )

    donnees_brutes = models.JSONField(
        default=dict,
        blank=True,
        help_text="Copie brute du dictionnaire extrait du HTML/crawler"
    )

    metadonnees = models.JSONField(
        default=dict,
        blank=True
    )

    class Meta:
        db_table = "resultats"
        ordering = ["-date_publication"]
        indexes = [
            models.Index(fields=["statut", "date_publication"]),
        ]

    def __str__(self):
        return f"Résultat - {self.course}"

    @property
    def est_officiel(self):
        return self.statut == self.Statut.OFFICIEL

    def set_arrivee_depuis_liste(self, liste_chevaux: list[str]) -> None:
        """
        Transforme une liste simple ['14', '3', '5', '6', '12']
        en liste d'objets avec un rang incrémental 1...N
        """
        self.arrivee = [
            {"rang": idx, "cheval": str(numero).strip()}
            for idx, numero in enumerate(liste_chevaux, start=1)
        ]