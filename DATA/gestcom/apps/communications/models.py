from django.db import models
from django.utils import timezone
from apps.core.models import ModeleAuditable


class Communique(ModeleAuditable):
    class Type(models.TextChoices):
        INFORMATION = "INFORMATION", "Information"
        ANNONCE = "ANNONCE", "Annonce"
        ALERTE = "ALERTE", "Alerte"
        RESULTAT = "RESULTAT", "Résultat"
        PROGRAMME = "PROGRAMME", "Programme"
        PROMOTION = "PROMOTION", "Promotion"
        AUTRE = "AUTRE", "Autre"

    class Statut(models.TextChoices):
        BROUILLON = "BROUILLON", "Brouillon"
        PROGRAMME = "PROGRAMME", "Programmé"
        PUBLIE = "PUBLIE", "Publié"
        ARCHIVE = "ARCHIVE", "Archivé"

    titre = models.CharField(
        max_length=255,
        verbose_name="Titre"
    )

    resume = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="Résumé"
    )

    contenu = models.TextField(
        verbose_name="Contenu"
    )

    type = models.CharField(
        max_length=30,
        choices=Type.choices,
        default=Type.INFORMATION,
        db_index=True
    )

    statut = models.CharField(
        max_length=20,
        choices=Statut.choices,
        default=Statut.BROUILLON,
        db_index=True
    )

    image = models.ImageField(
        upload_to="communications/",
        blank=True,
        null=True
    )

    date_publication = models.DateTimeField(
        blank=True,
        null=True,
        db_index=True
    )

    date_expiration = models.DateTimeField(
        blank=True,
        null=True,
        db_index=True
    )

    est_a_la_une = models.BooleanField(
        default=False,
        db_index=True
    )

    ordre_affichage = models.PositiveIntegerField(
        default=0
    )

    nombre_vues = models.PositiveIntegerField(
        default=0
    )

    # Permet de stocker ultérieurement des informations
    # complémentaires sans modifier immédiatement le schéma.
    metadonnees = models.JSONField(
        default=dict,
        blank=True
    )

    class Meta:
        db_table = "communications"
        ordering = ["-est_a_la_une", "-ordre_affichage", "-date_publication"]
        indexes = [
            models.Index(fields=["statut", "date_publication"]),
            models.Index(fields=["type", "statut"]),
            models.Index(fields=["est_a_la_une", "statut"]),
        ]

    def __str__(self):
        return self.titre

    @property
    def est_actuellement_publie(self):
        maintenant = timezone.now()

        if self.statut != self.Statut.PUBLIE:
            return False

        if self.date_publication and self.date_publication > maintenant:
            return False

        if self.date_expiration and self.date_expiration < maintenant:
            return False

        return True