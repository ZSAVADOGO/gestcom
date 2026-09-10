from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone

from apps.core.models import ModeleAuditable
from apps.hippisme.models import Course
from apps.points_vente.models import PointVente


class Pari(ModeleAuditable):

    class Type(models.TextChoices):
        SIMPLE = "SIMPLE", "Simple"
        COUPLE = "COUPLE", "Couplé"
        TIERCE = "TIERCE", "Tiercé"
        QUARTE = "QUARTE", "Quarté"
        QUINTE = "QUINTE", "Quinté"
        AUTRE = "AUTRE", "Autre"

    class Statut(models.TextChoices):
        EN_ATTENTE = "EN_ATTENTE", "En attente"
        GAGNANT = "GAGNANT", "Gagnant"
        PERDANT = "PERDANT", "Perdant"
        ANNULE = "ANNULE", "Annulé"
        REMBOURSE = "REMBOURSE", "Remboursé"
        VERIFIE = "VERIFIE", "Vérifié"

    numero_ticket = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        verbose_name="Numéro du ticket"
    )

    type = models.CharField(
        max_length=20,
        choices=Type.choices,
        db_index=True
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.PROTECT,
        related_name="paris",
        verbose_name="Course"
    )

    point_vente = models.ForeignKey(
        PointVente,
        on_delete=models.PROTECT,
        related_name="paris",
        null=True,
        blank=True
    )

    montant_mise = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Mise"
    )

    montant_gain = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Gain"
    )

    selections = models.JSONField(
        default=list,
        verbose_name="Sélections"
    )

    statut = models.CharField(
        max_length=20,
        choices=Statut.choices,
        default=Statut.EN_ATTENTE,
        db_index=True
    )

    est_verifie = models.BooleanField(
        default=False,
        db_index=True
    )

    date_prise = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True
    )

    date_verification = models.DateTimeField(
        null=True,
        blank=True
    )

    date_paiement = models.DateTimeField(
        null=True,
        blank=True
    )

    motif_annulation = models.CharField(
        max_length=255,
        blank=True
    )

    reference_externe = models.CharField(
        max_length=100,
        blank=True,
        db_index=True
    )

    # Permet de conserver des informations supplémentaires
    # sans modifier la structure relationnelle.
    donnees_ticket = models.JSONField(
        default=dict,
        blank=True
    )

    metadonnees = models.JSONField(
        default=dict,
        blank=True
    )

    class Meta:
        db_table = "paris"

        ordering = ["-date_prise"]

        indexes = [
            models.Index(fields=["course", "statut"]),
            models.Index(fields=["point_vente", "date_prise"]),
            models.Index(fields=["est_verifie", "statut"]),
            models.Index(fields=["type", "statut"]),
        ]

    def __str__(self):
        return self.numero_ticket

    @property
    def est_gagnant(self):
        return self.statut == self.Statut.GAGNANT

    @property
    def est_perdant(self):
        return self.statut == self.Statut.PERDANT

    def marquer_verifie(self, statut, gain=0):
        self.statut = statut
        self.est_verifie = True
        self.montant_gain = gain
        self.date_verification = timezone.now()
        self.save(
            update_fields=[
                "statut",
                "est_verifie",
                "montant_gain",
                "date_verification",
                "date_modification",
            ]
        )