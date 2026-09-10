from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import ProtectedError
from django.urls import reverse_lazy
from django.urls import reverse

from datetime import datetime
from django.db import transaction
from django.utils.text import slugify


from django.views.generic import (
    TemplateView,
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)

from .models import (
    Hippodrome,
    Entraineur,
    Jockey,
    Cheval,
    Reunion,
    Course,
    Partant,
)

from .forms import (
    HippodromeForm,
    EntraineurForm,
    JockeyForm,
    ChevalForm,
    ReunionForm,
    CourseForm,
    PartantForm,
)

from .services import HippismeService

from django.conf import settings


# ✅ Définir un mixin vide si DEBUG est True
class DummyMixin:
    pass


# Si DEBUG est True (Dev), le mixin ne fait rien (object).
# Si DEBUG est False (Prod), LoginRequiredMixin s'applique.
DevLoginRequiredMixin = LoginRequiredMixin if not settings.DEBUG else DummyMixin




# UTILISATIO DU CRAWLER



@transaction.atomic
def inserer_programme_lonab(data_page_web: dict):
    """
    Exemple de structure `data_page_web` issue du scraper :
    {
        "hippodrome": "Vincennes",
        "date_reunion": "2026-09-09",
        "numero_reunion": 1,
        "course_numero": 1,
        "course_nom": "Prix de la Cote d'Or",
        "distance": 2700,
        "discipline": "ATTELE",
        "heure_depart": "13:50",
        "partants": [
            {
                "numero": 1,
                "cheval": "FLAMME DU GOUTIER",
                "sexe": "FEMELLE",
                "jockey": "E. RAFFIN",
                "entraineur": "TH. DUVALDESTIN",
                "musique": "1m (25) 2a"
            },
            ...
        ]
    }
    """
    # 1. Hippodrome
    nom_hippo = data_page_web.get("hippodrome", "Inconnu")
    hippodrome_obj, _ = Hippodrome.objects.get_or_create(
        code=slugify(nom_hippo).upper(),
        defaults={"nom": nom_hippo, "ville": nom_hippo}
    )

    # 2. Réunion
    date_dt = datetime.strptime(data_page_web["date_reunion"], "%Y-%m-%d").date()
    num_reunion = data_page_web.get("numero_reunion", 1)
    code_reunion = f"R{num_reunion}-{date_dt.strftime('%Y%m%d')}"

    reunion_obj, _ = Reunion.objects.get_or_create(
        code=code_reunion,
        defaults={
            "hippodrome": hippodrome_obj,
            "date_reunion": date_dt,
            "numero": num_reunion,
            "nom": f"Réunion {num_reunion} - {nom_hippo}"
        }
    )

    # 3. Course
    num_course = data_page_web["course_numero"]
    code_course = f"{code_reunion}-C{num_course}"

    course_obj, _ = Course.objects.update_or_create(
        code=code_course,
        defaults={
            "reunion": reunion_obj,
            "numero": num_course,
            "nom": data_page_web.get("course_nom", f"Course {num_course}"),
            "distance_metres": data_page_web.get("distance", 2000),
            "categorie": data_page_web.get("discipline", Course.Categorie.PLAT),
            "heure_depart": data_page_web.get("heure_depart"),
            "nombre_partants_prevu": len(data_page_web.get("partants", []))
        }
    )

    # 4. Partants, Chevaux, Jockeys & Entraîneurs
    for item in data_page_web.get("partants", []):
        # Entraîneur
        entraineur_obj = None
        if item.get("entraineur"):
            code_e = slugify(item["entraineur"])
            entraineur_obj, _ = Entraineur.objects.get_or_create(
                code=code_e,
                defaults={"nom_complet": item["entraineur"]}
            )

        # Jockey
        jockey_obj = None
        if item.get("jockey"):
            code_j = slugify(item["jockey"])
            jockey_obj, _ = Jockey.objects.get_or_create(
                code=code_j,
                defaults={"nom_complet": item["jockey"]}
            )

        # Cheval
        nom_cheval = item["cheval"].strip().upper()
        cheval_obj, _ = Cheval.objects.get_or_create(
            numero_enregistrement=slugify(nom_cheval),
            defaults={
                "nom": nom_cheval,
                "sexe": item.get("sexe", Cheval.Sexe.INCONNU),
                "entraineur_actuel": entraineur_obj
            }
        )

        # Association Partant
        Partant.objects.update_or_create(
            course=course_obj,
            numero=item["numero"],
            defaults={
                "cheval": cheval_obj,
                "jockey": jockey_obj,
                "entraineur": entraineur_obj,
                "donnees_source": {"musique": item.get("musique", "")}
            }
        )

    return course_obj

# ============================================================
# ACCUEIL
# ============================================================


class HippismeAccueilView(DevLoginRequiredMixin, TemplateView):

    template_name = "hippisme/accueil.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["statistiques"] = HippismeService.statistiques()

        context["reunions_du_jour"] = HippismeService.reunions_du_jour()

        context["courses_du_jour"] = HippismeService.courses_du_jour()

        return context


# ============================================================
# HIPPODROMES
# ============================================================


class HippodromeListView(DevLoginRequiredMixin, ListView):

    template_name = "hippisme/liste.html"
    context_object_name = "objets"
    paginate_by = 20

    def get_queryset(self):
        return HippismeService.liste_hippodromes(
            recherche=self.request.GET.get("q"),
            ville=self.request.GET.get("ville"),
            actifs_seulement=False,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update(
            {
                "titre": "Hippodromes",
                "sous_titre": "Gestion des hippodromes",
                "type_objet": "hippodrome",
                "url_creation": "hippisme:hippodrome-creer",
                "colonnes": [
                    ("code", "Code"),
                    ("nom", "Nom"),
                    ("ville", "Ville"),
                    ("pays", "Pays"),
                    ("est_actif", "Actif"),
                ],
            }
        )

        return context


class HippodromeDetailView(DevLoginRequiredMixin, DetailView):

    model = Hippodrome
    template_name = "hippisme/detail.html"
    context_object_name = "objet"

    def get_queryset(self):
        return Hippodrome.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update(
            {
                "titre": self.object.nom,
                "type_objet": "hippodrome",
                "url_modification": ("hippisme:hippodrome-modifier"),
                "url_suppression": ("hippisme:hippodrome-supprimer"),
            }
        )

        return context


class HippodromeCreateView(DevLoginRequiredMixin, CreateView):

    model = Hippodrome
    form_class = HippodromeForm
    template_name = "hippisme/formulaire.html"
    success_url = reverse_lazy("hippisme:hippodromes")

    def form_valid(self, form):
        objet = HippismeService.creer_hippodrome(form.cleaned_data)

        self.object = objet

        messages.success(self.request, "Hippodrome créé avec succès.")

        return super().form_valid(form)


class HippodromeUpdateView(DevLoginRequiredMixin, UpdateView):

    model = Hippodrome
    form_class = HippodromeForm
    template_name = "hippisme/formulaire.html"
    success_url = reverse_lazy("hippisme:hippodromes")

    def form_valid(self, form):
        HippismeService.modifier_hippodrome(self.object, form.cleaned_data)

        messages.success(self.request, "Hippodrome modifié avec succès.")

        return super().form_valid(form)


class HippodromeDeleteView(DevLoginRequiredMixin, DeleteView):

    model = Hippodrome
    template_name = "hippisme/confirmation_suppression.html"
    success_url = reverse_lazy("hippisme:hippodromes")

    def form_valid(self, form):
        try:
            HippismeService.supprimer_hippodrome(self.object)

            messages.success(self.request, "Hippodrome supprimé avec succès.")

            return super().form_valid(form)

        except ProtectedError:
            messages.error(
                self.request,
                "Impossible de supprimer cet hippodrome "
                "car il est utilisé par une réunion.",
            )

            return self.get(self.request, *self.args, **self.kwargs)


# ============================================================
# ENTRAÎNEURS
# ============================================================


class EntraineurListView(DevLoginRequiredMixin, ListView):

    template_name = "hippisme/liste.html"
    context_object_name = "objets"
    paginate_by = 20

    def get_queryset(self):
        return HippismeService.liste_entraineurs(
            recherche=self.request.GET.get("q"),
            actifs_seulement=False,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update(
            {
                "titre": "Entraîneurs",
                "sous_titre": "Gestion des entraîneurs",
                "type_objet": "entraineur",
                "url_creation": "hippisme:entraineur-creer",
                "colonnes": [
                    ("code", "Code"),
                    ("nom_complet", "Nom complet"),
                    ("pays", "Pays"),
                    ("telephone", "Téléphone"),
                    ("est_actif", "Actif"),
                ],
            }
        )

        return context


class EntraineurDetailView(DevLoginRequiredMixin, DetailView):

    model = Entraineur
    template_name = "hippisme/detail.html"
    context_object_name = "objet"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update(
            {
                "titre": self.object.nom_complet,
                "type_objet": "entraineur",
                "url_modification": "hippisme:entraineur-modifier",
                "url_suppression": "hippisme:entraineur-supprimer",
            }
        )

        return context


class EntraineurCreateView(DevLoginRequiredMixin, CreateView):

    model = Entraineur
    form_class = EntraineurForm
    template_name = "hippisme/formulaire.html"
    success_url = reverse_lazy("hippisme:entraineurs")

    def form_valid(self, form):
        self.object = HippismeService.creer_entraineur(form.cleaned_data)

        messages.success(self.request, "Entraîneur créé avec succès.")

        return super().form_valid(form)


class EntraineurUpdateView(DevLoginRequiredMixin, UpdateView):

    model = Entraineur
    form_class = EntraineurForm
    template_name = "hippisme/formulaire.html"
    success_url = reverse_lazy("hippisme:entraineurs")

    def form_valid(self, form):
        HippismeService.modifier_entraineur(self.object, form.cleaned_data)

        messages.success(self.request, "Entraîneur modifié avec succès.")

        return super().form_valid(form)


class EntraineurDeleteView(DevLoginRequiredMixin, DeleteView):

    model = Entraineur
    template_name = "hippisme/confirmation_suppression.html"
    success_url = reverse_lazy("hippisme:entraineurs")


# ============================================================
# JOCKEYS
# ============================================================


class JockeyListView(DevLoginRequiredMixin, ListView):

    template_name = "hippisme/liste.html"
    context_object_name = "objets"
    paginate_by = 20

    def get_queryset(self):
        return HippismeService.liste_jockeys(
            recherche=self.request.GET.get("q"),
            actifs_seulement=False,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update(
            {
                "titre": "Jockeys",
                "sous_titre": "Gestion des jockeys",
                "type_objet": "jockey",
                "url_creation": "hippisme:jockey-creer",
                "colonnes": [
                    ("code", "Code"),
                    ("nom_complet", "Nom complet"),
                    ("pays", "Pays"),
                    ("poids_reference_kg", "Poids référence"),
                    ("est_actif", "Actif"),
                ],
            }
        )

        return context


class JockeyDetailView(DevLoginRequiredMixin, DetailView):

    model = Jockey
    template_name = "hippisme/detail.html"
    context_object_name = "objet"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update(
            {
                "titre": self.object.nom_complet,
                "type_objet": "jockey",
                "url_modification": "hippisme:jockey-modifier",
                "url_suppression": "hippisme:jockey-supprimer",
            }
        )

        return context


class JockeyCreateView(DevLoginRequiredMixin, CreateView):

    model = Jockey
    form_class = JockeyForm
    template_name = "hippisme/formulaire.html"
    success_url = reverse_lazy("hippisme:jockeys")

    def form_valid(self, form):
        self.object = HippismeService.creer_jockey(form.cleaned_data)

        messages.success(self.request, "Jockey créé avec succès.")

        return super().form_valid(form)


class JockeyUpdateView(DevLoginRequiredMixin, UpdateView):

    model = Jockey
    form_class = JockeyForm
    template_name = "hippisme/formulaire.html"
    success_url = reverse_lazy("hippisme:jockeys")

    def form_valid(self, form):
        HippismeService.modifier_jockey(self.object, form.cleaned_data)

        messages.success(self.request, "Jockey modifié avec succès.")

        return super().form_valid(form)


class JockeyDeleteView(DevLoginRequiredMixin, DeleteView):

    model = Jockey
    template_name = "hippisme/confirmation_suppression.html"
    success_url = reverse_lazy("hippisme:jockeys")


# ============================================================
# CHEVAUX
# ============================================================


class ChevalListView(DevLoginRequiredMixin, ListView):

    template_name = "hippisme/liste.html"
    context_object_name = "objets"
    paginate_by = 20

    def get_queryset(self):
        return HippismeService.liste_chevaux(
            recherche=self.request.GET.get("q"),
            sexe=self.request.GET.get("sexe"),
            entraineur=self.request.GET.get("entraineur"),
            actifs_seulement=False,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update(
            {
                "titre": "Chevaux",
                "sous_titre": "Gestion des chevaux",
                "type_objet": "cheval",
                "url_creation": "hippisme:cheval-creer",
                "colonnes": [
                    ("numero_enregistrement", "N°"),
                    ("nom", "Nom"),
                    ("sexe", "Sexe"),
                    ("race", "Race"),
                    ("couleur", "Couleur"),
                    ("entraineur_actuel", "Entraîneur"),
                    ("est_actif", "Actif"),
                ],
            }
        )

        return context


def construire_informations_cheval(cheval):
    return [
        {
            "label": "Numéro d'enregistrement",
            "valeur": cheval.numero_enregistrement,
        },
        {
            "label": "Nom",
            "valeur": cheval.nom,
        },
        {
            "label": "Sexe",
            "valeur": cheval.get_sexe_display(),
        },
        {
            "label": "Race",
            "valeur": cheval.race,
        },
        {
            "label": "Entraîneur",
            "valeur": (
                cheval.entraineur_actuel.nom_complet
                if cheval.entraineur_actuel
                else "-"
            ),
        },
        {
            "label": "Propriétaire",
            "valeur": cheval.proprietaire or "-",
        },
        {
            "label": "Date de naissance",
            "valeur": cheval.date_naissance,
        },
        {
            "label": "Couleur",
            "valeur": cheval.couleur or "-",
        },
        {
            "label": "Statut",
            "valeur": "Actif" if cheval.est_actif else "Inactif",
        },
    ]


class ChevalDetailView(DevLoginRequiredMixin, DetailView):
    model = Cheval
    template_name = "hippisme/detail.html"
    context_object_name = "objet"

    def get_queryset(self):
        return Cheval.objects.select_related("entraineur_actuel")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        cheval = self.object

        context.update(
            {
                "titre": "Fiche du cheval",
                "sous_titre": cheval.nom,
                "icone": "fas fa-horse-head",
                "informations": construire_informations_cheval(cheval),
                "retour_url": reverse("hippisme:chevaux"),
                "url_modifier": reverse(
                    "hippisme:cheval_modifier", kwargs={"pk": cheval.pk}
                ),
                "url_supprimer": reverse(
                    "hippisme:cheval_supprimer", kwargs={"pk": cheval.pk}
                ),
                "audit": {
                    "date_creation": cheval.date_creation,
                    "date_modification": cheval.date_modification,
                    "cree_par": cheval.cree_par,
                    "modifie_par": cheval.modifie_par,
                },
            }
        )

        return context


""" class ChevalDetailView(DevLoginRequiredMixin, DetailView):

    model = Cheval
    template_name = "hippisme/detail.html"
    context_object_name = "objet"

    def get_queryset(self):
        return Cheval.objects.select_related(
            "entraineur_actuel"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({
            "titre": self.object.nom,
            "type_objet": "cheval",
            "url_modification": "hippisme:cheval-modifier",
            "url_suppression": "hippisme:cheval-supprimer",
        })

        return context """


class ChevalCreateView(DevLoginRequiredMixin, CreateView):

    model = Cheval
    form_class = ChevalForm
    template_name = "hippisme/formulaire.html"
    success_url = reverse_lazy("hippisme:chevaux")

    def form_valid(self, form):
        self.object = HippismeService.creer_cheval(form.cleaned_data)

        messages.success(self.request, "Cheval créé avec succès.")

        return super().form_valid(form)


class ChevalUpdateView(DevLoginRequiredMixin, UpdateView):

    model = Cheval
    form_class = ChevalForm
    template_name = "hippisme/formulaire.html"
    success_url = reverse_lazy("hippisme:chevaux")

    def form_valid(self, form):
        HippismeService.modifier_cheval(self.object, form.cleaned_data)

        messages.success(self.request, "Cheval modifié avec succès.")

        return super().form_valid(form)


class ChevalDeleteView(DevLoginRequiredMixin, DeleteView):

    model = Cheval
    template_name = "hippisme/confirmation_suppression.html"
    success_url = reverse_lazy("hippisme:chevaux")


# ============================================================
# RÉUNIONS
# ============================================================


class ReunionListView(DevLoginRequiredMixin, ListView):

    template_name = "hippisme/liste.html"
    context_object_name = "objets"
    paginate_by = 20

    def get_queryset(self):
        return HippismeService.liste_reunions(
            date_reunion=self.request.GET.get("date"),
            hippodrome=self.request.GET.get("hippodrome"),
            statut=self.request.GET.get("statut"),
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update(
            {
                "titre": "Réunions",
                "sous_titre": "Programme des réunions",
                "type_objet": "reunion",
                "url_creation": "hippisme:reunion-creer",
                "colonnes": [
                    ("code", "Code"),
                    ("numero", "N°"),
                    ("nom", "Réunion"),
                    ("hippodrome", "Hippodrome"),
                    ("date_reunion", "Date"),
                    ("heure_debut", "Heure"),
                    ("statut", "Statut"),
                    ("nombre_courses", "Courses"),
                ],
            }
        )

        return context


class ReunionDetailView(DevLoginRequiredMixin, DetailView):

    model = Reunion
    template_name = "hippisme/detail.html"
    context_object_name = "objet"

    def get_queryset(self):
        return Reunion.objects.select_related("hippodrome").prefetch_related("courses")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update(
            {
                "titre": self.object.nom,
                "type_objet": "reunion",
                "url_modification": "hippisme:reunion-modifier",
                "url_suppression": "hippisme:reunion-supprimer",
                "courses": self.object.courses.all(),
            }
        )

        return context


class ReunionCreateView(DevLoginRequiredMixin, CreateView):

    model = Reunion
    form_class = ReunionForm
    template_name = "hippisme/formulaire.html"
    success_url = reverse_lazy("hippisme:reunions")

    def form_valid(self, form):
        self.object = HippismeService.creer_reunion(form.cleaned_data)

        messages.success(self.request, "Réunion créée avec succès.")

        return super().form_valid(form)


class ReunionUpdateView(DevLoginRequiredMixin, UpdateView):

    model = Reunion
    form_class = ReunionForm
    template_name = "hippisme/formulaire.html"
    success_url = reverse_lazy("hippisme:reunions")

    def form_valid(self, form):
        HippismeService.modifier_reunion(self.object, form.cleaned_data)

        messages.success(self.request, "Réunion modifiée avec succès.")

        return super().form_valid(form)


class ReunionDeleteView(DevLoginRequiredMixin, DeleteView):

    model = Reunion
    template_name = "hippisme/confirmation_suppression.html"
    success_url = reverse_lazy("hippisme:reunions")


# ============================================================
# COURSES
# ============================================================


class CourseListView(DevLoginRequiredMixin, ListView):

    template_name = "hippisme/liste.html"
    context_object_name = "objets"
    paginate_by = 20

    def get_queryset(self):
        return HippismeService.liste_courses(
            recherche=self.request.GET.get("q"),
            reunion=self.request.GET.get("reunion"),
            date_reunion=self.request.GET.get("date"),
            statut=self.request.GET.get("statut"),
            categorie=self.request.GET.get("categorie"),
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update(
            {
                "titre": "Courses",
                "sous_titre": "Programme des courses",
                "type_objet": "course",
                "url_creation": "hippisme:course-creer",
                "colonnes": [
                    ("numero", "N°"),
                    ("code", "Code"),
                    ("nom", "Course"),
                    ("reunion", "Réunion"),
                    ("categorie", "Catégorie"),
                    ("distance_metres", "Distance"),
                    ("heure_depart", "Départ"),
                    ("statut", "Statut"),
                ],
            }
        )

        return context


class CourseDetailView(DevLoginRequiredMixin, DetailView):

    model = Course
    template_name = "hippisme/detail.html"
    context_object_name = "objet"

    def get_queryset(self):
        return Course.objects.select_related(
            "reunion",
            "reunion__hippodrome",
        ).prefetch_related(
            "partants__cheval",
            "partants__jockey",
            "partants__entraineur",
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update(
            {
                "titre": self.object.nom,
                "type_objet": "course",
                "url_modification": "hippisme:course-modifier",
                "url_suppression": "hippisme:course-supprimer",
                "partants": self.object.partants.all(),
            }
        )

        return context


class CourseCreateView(DevLoginRequiredMixin, CreateView):

    model = Course
    form_class = CourseForm
    template_name = "hippisme/formulaire.html"
    success_url = reverse_lazy("hippisme:courses")

    def form_valid(self, form):
        self.object = HippismeService.creer_course(form.cleaned_data)

        messages.success(self.request, "Course créée avec succès.")

        return super().form_valid(form)


class CourseUpdateView(DevLoginRequiredMixin, UpdateView):

    model = Course
    form_class = CourseForm
    template_name = "hippisme/formulaire.html"
    success_url = reverse_lazy("hippisme:courses")

    def form_valid(self, form):
        HippismeService.modifier_course(self.object, form.cleaned_data)

        messages.success(self.request, "Course modifiée avec succès.")

        return super().form_valid(form)


class CourseDeleteView(DevLoginRequiredMixin, DeleteView):

    model = Course
    template_name = "hippisme/confirmation_suppression.html"
    success_url = reverse_lazy("hippisme:courses")


# ============================================================
# PARTANTS
# ============================================================


class PartantListView(DevLoginRequiredMixin, ListView):

    template_name = "hippisme/liste.html"
    context_object_name = "objets"
    paginate_by = 30

    def get_queryset(self):
        return HippismeService.liste_partants(
            course=self.request.GET.get("course"),
            cheval=self.request.GET.get("cheval"),
            jockey=self.request.GET.get("jockey"),
            entraineur=self.request.GET.get("entraineur"),
            uniquement_partants=False,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update(
            {
                "titre": "Partants",
                "sous_titre": "Gestion des partants",
                "type_objet": "partant",
                "url_creation": "hippisme:partant-creer",
                "colonnes": [
                    ("numero", "N°"),
                    ("cheval", "Cheval"),
                    ("jockey", "Jockey"),
                    ("entraineur", "Entraîneur"),
                    ("poids_kg", "Poids"),
                    ("age", "Âge"),
                    ("cote", "Cote"),
                    ("est_non_partant", "NP"),
                ],
            }
        )

        return context


class PartantDetailView(DevLoginRequiredMixin, DetailView):

    model = Partant
    template_name = "hippisme/detail.html"
    context_object_name = "objet"

    def get_queryset(self):
        return Partant.objects.select_related(
            "course",
            "course__reunion",
            "cheval",
            "jockey",
            "entraineur",
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update(
            {
                "titre": (f"{self.object.numero} - " f"{self.object.cheval.nom}"),
                "type_objet": "partant",
                "url_modification": "hippisme:partant-modifier",
                "url_suppression": "hippisme:partant-supprimer",
            }
        )

        return context


class PartantCreateView(DevLoginRequiredMixin, CreateView):

    model = Partant
    form_class = PartantForm
    template_name = "hippisme/formulaire.html"
    success_url = reverse_lazy("hippisme:partants")

    def form_valid(self, form):
        self.object = HippismeService.creer_partant(form.cleaned_data)

        messages.success(self.request, "Partant créé avec succès.")

        return super().form_valid(form)


class PartantUpdateView(DevLoginRequiredMixin, UpdateView):

    model = Partant
    form_class = PartantForm
    template_name = "hippisme/formulaire.html"
    success_url = reverse_lazy("hippisme:partants")

    def form_valid(self, form):
        HippismeService.modifier_partant(self.object, form.cleaned_data)

        messages.success(self.request, "Partant modifié avec succès.")

        return super().form_valid(form)


class PartantDeleteView(DevLoginRequiredMixin, DeleteView):

    model = Partant
    template_name = "hippisme/confirmation_suppression.html"
    success_url = reverse_lazy("hippisme:partants")
