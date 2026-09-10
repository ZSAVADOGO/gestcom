from django import forms

from .models import (
    Hippodrome,
    Entraineur,
    Jockey,
    Cheval,
    Reunion,
    Course,
    Partant,
)


class StyleFormMixin:
    """
    Applique automatiquement le style Tailwind aux champs.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            classe = (
                "w-full rounded-lg border border-gray-300 "
                "px-4 py-2.5 focus:border-indigo-500 "
                "focus:ring-2 focus:ring-indigo-200 "
                "outline-none"
            )

            if isinstance(
                field.widget,
                (
                    forms.Textarea,
                    forms.Select,
                    forms.SelectMultiple
                )
            ):
                field.widget.attrs["class"] = classe
            else:
                field.widget.attrs["class"] = classe


class HippodromeForm(StyleFormMixin, forms.ModelForm):

    class Meta:
        model = Hippodrome
        fields = [
            "code",
            "nom",
            "ville",
            "pays",
            "adresse",
            "latitude",
            "longitude",
            "description",
            "est_actif",
            "metadonnees",
        ]

        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "metadonnees": forms.Textarea(attrs={"rows": 4}),
        }


class EntraineurForm(StyleFormMixin, forms.ModelForm):

    class Meta:
        model = Entraineur
        fields = [
            "code",
            "nom_complet",
            "pays",
            "telephone",
            "email",
            "date_naissance",
            "est_actif",
            "metadonnees",
        ]

        widgets = {
            "date_naissance": forms.DateInput(
                attrs={"type": "date"}
            ),
            "metadonnees": forms.Textarea(attrs={"rows": 4}),
        }


class JockeyForm(StyleFormMixin, forms.ModelForm):

    class Meta:
        model = Jockey
        fields = [
            "code",
            "nom_complet",
            "pays",
            "date_naissance",
            "poids_reference_kg",
            "est_actif",
            "metadonnees",
        ]

        widgets = {
            "date_naissance": forms.DateInput(
                attrs={"type": "date"}
            ),
            "metadonnees": forms.Textarea(attrs={"rows": 4}),
        }


class ChevalForm(StyleFormMixin, forms.ModelForm):

    class Meta:
        model = Cheval
        fields = [
            "numero_enregistrement",
            "nom",
            "sexe",
            "date_naissance",
            "race",
            "couleur",
            "proprietaire",
            "entraineur_actuel",
            "observations",
            "est_actif",
            "metadonnees",
        ]

        widgets = {
            "date_naissance": forms.DateInput(
                attrs={"type": "date"}
            ),
            "observations": forms.Textarea(
                attrs={"rows": 4}
            ),
            "metadonnees": forms.Textarea(
                attrs={"rows": 4}
            ),
        }

        labels = {
            "numero_enregistrement": "N° d'enregistrement",
            "entraineur_actuel": "Entraîneur actuel",
        }


class ReunionForm(StyleFormMixin, forms.ModelForm):

    class Meta:
        model = Reunion
        fields = [
            "code",
            "numero",
            "nom",
            "hippodrome",
            "date_reunion",
            "heure_debut",
            "statut",
            "nombre_courses_prevu",
            "nombre_courses_terminees",
            "description",
            "metadonnees",
        ]

        widgets = {
            "date_reunion": forms.DateInput(
                attrs={"type": "date"}
            ),
            "heure_debut": forms.TimeInput(
                attrs={"type": "time"}
            ),
            "description": forms.Textarea(
                attrs={"rows": 4}
            ),
            "metadonnees": forms.Textarea(
                attrs={"rows": 4}
            ),
        }


class CourseForm(StyleFormMixin, forms.ModelForm):

    class Meta:
        model = Course
        fields = [
            "reunion",
            "numero",
            "code",
            "nom",
            "categorie",
            "distance_metres",
            "nombre_partants_prevu",
            "heure_depart",
            "heure_depart_reelle",
            "statut",
            "est_active",
            "conditions",
            "allocation",
            "commentaire",
            "metadonnees",
        ]

        widgets = {
            "heure_depart": forms.TimeInput(
                attrs={"type": "time"}
            ),
            "heure_depart_reelle": forms.TimeInput(
                attrs={"type": "time"}
            ),
            "conditions": forms.Textarea(
                attrs={"rows": 4}
            ),
            "commentaire": forms.Textarea(
                attrs={"rows": 4}
            ),
            "metadonnees": forms.Textarea(
                attrs={"rows": 4}
            ),
        }


class PartantForm(StyleFormMixin, forms.ModelForm):

    class Meta:
        model = Partant
        fields = [
            "course",
            "cheval",
            "jockey",
            "entraineur",
            "numero",
            "corde",
            "poids_kg",
            "age",
            "cote",
            "est_non_partant",
            "raison_non_partant",
            "observations",
            "donnees_source",
        ]

        widgets = {
            "raison_non_partant": forms.Textarea(
                attrs={"rows": 3}
            ),
            "observations": forms.Textarea(
                attrs={"rows": 3}
            ),
            "donnees_source": forms.Textarea(
                attrs={"rows": 4}
            ),
        }