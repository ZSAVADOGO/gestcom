from django.db import models

from apps.core.models import ModeleAuditable


class PointVente(ModeleAuditable):
    class Type(models.TextChoices):
        AGENCE = "AGENCE", "Agence"
        POINT_VENTE = "POINT_VENTE", "Point de vente"
        PMU_CLUB = "PMU_CLUB", "PMU Club"
        AUTRE = "AUTRE", "Autre"

    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Code"
    )

    nom = models.CharField(
        max_length=150,
        verbose_name="Nom"
    )

    type = models.CharField(
        max_length=30,
        choices=Type.choices,
        default=Type.POINT_VENTE,
        db_index=True
    )

    ville = models.CharField(
        max_length=100,
        default="Ouagadougou",
        db_index=True
    )

    quartier = models.CharField(
        max_length=150,
        blank=True,
        db_index=True
    )

    adresse = models.CharField(
        max_length=255,
        blank=True
    )

    description = models.TextField(
        blank=True
    )

    telephone = models.CharField(
        max_length=30,
        blank=True
    )

    email = models.EmailField(
        blank=True
    )

    horaires = models.JSONField(
        default=dict,
        blank=True
    )

    latitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True
    )

    longitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True
    )

    # Services disponibles dans le point de vente.
    services = models.JSONField(
        default=list,
        blank=True
    )

    est_actif = models.BooleanField(
        default=True,
        db_index=True
    )

    est_principal = models.BooleanField(
        default=False,
        db_index=True
    )

    date_ouverture = models.DateField(
        null=True,
        blank=True
    )

    metadonnees = models.JSONField(
        default=dict,
        blank=True
    )

    class Meta:
        db_table = "points_vente"
        ordering = ["ville", "quartier", "nom"]

        indexes = [
            models.Index(fields=["ville", "quartier"]),
            models.Index(fields=["est_actif", "ville"]),
            models.Index(fields=["latitude", "longitude"]),
        ]

    def __str__(self):
        return f"{self.nom} - {self.ville}"

    @property
    def possede_geolocalisation(self):
        return (
            self.latitude is not None
            and self.longitude is not None
        )