from django.conf import settings
from django.db import models

from .middleware import obtenir_utilisateur_courant


class ModeleAuditable(models.Model):

    created_at = models.DateTimeField(
        "Date de création",
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        "Date de modification",
        auto_now=True
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_crees"
    )

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_modifies"
    )

    def save(self, *args, **kwargs):

        utilisateur = obtenir_utilisateur_courant()

        if utilisateur and utilisateur.is_authenticated:

            if not self.pk and not self.created_by:
                self.created_by = utilisateur

            self.updated_by = utilisateur

        super().save(*args, **kwargs)

    class Meta:
        abstract = True