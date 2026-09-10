from django.conf import settings
from django.db import models


# ============================================================
# MODÈLE DE BASE
# ============================================================

class ModeleHippisme(models.Model):
    """
    Modèle abstrait commun aux entités hippiques.
    """
    date_creation = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création"
    )
    date_modification = models.DateTimeField(
        auto_now=True,
        verbose_name="Date de modification"
    )

    class Meta:
        abstract = True


# ============================================================
# HIPPODROME
# ============================================================

class Hippodrome(ModeleHippisme):
    code = models.CharField(
        max_length=50,
        blank=True,
        db_index=True,
        verbose_name="Code"
    )
    nom = models.CharField(
        max_length=150,
        verbose_name="Nom"
    )
    ville = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        verbose_name="Ville"
    )
    pays = models.CharField(
        max_length=100,
        default="Burkina Faso",
        blank=True,
        verbose_name="Pays"
    )
    adresse = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Adresse"
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
    description = models.TextField(
        blank=True,
        verbose_name="Description"
    )
    est_actif = models.BooleanField(
        default=True,
        db_index=True
    )
    metadonnees = models.JSONField(
        default=dict,
        blank=True
    )

    class Meta:
        db_table = "hippodromes"
        ordering = ["nom"]

    def __str__(self):
        return self.nom or f"Hippodrome #{self.pk}"


# ============================================================
# ENTRAINEUR
# ============================================================

class Entraineur(ModeleHippisme):
    code = models.CharField(
        max_length=50,
        blank=True,
        db_index=True
    )
    nom_complet = models.CharField(
        max_length=150,
        db_index=True,
        verbose_name="Nom complet"
    )
    pays = models.CharField(
        max_length=100,
        default="Burkina Faso",
        blank=True
    )
    telephone = models.CharField(
        max_length=30,
        blank=True
    )
    email = models.CharField(
        max_length=254,
        blank=True
    )
    date_naissance = models.DateField(
        null=True,
        blank=True
    )
    est_actif = models.BooleanField(
        default=True,
        db_index=True
    )
    metadonnees = models.JSONField(
        default=dict,
        blank=True
    )

    class Meta:
        db_table = "entraineurs"
        ordering = ["nom_complet"]

    def __str__(self):
        return self.nom_complet or f"Entraineur #{self.pk}"


# ============================================================
# JOCKEY
# ============================================================

class Jockey(ModeleHippisme):
    code = models.CharField(
        max_length=50,
        blank=True,
        db_index=True
    )
    nom_complet = models.CharField(
        max_length=150,
        db_index=True,
        verbose_name="Nom complet"
    )
    pays = models.CharField(
        max_length=100,
        default="Burkina Faso",
        blank=True
    )
    date_naissance = models.DateField(
        null=True,
        blank=True
    )
    poids_reference_kg = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    est_actif = models.BooleanField(
        default=True,
        db_index=True
    )
    metadonnees = models.JSONField(
        default=dict,
        blank=True
    )

    class Meta:
        db_table = "jockeys"
        ordering = ["nom_complet"]

    def __str__(self):
        return self.nom_complet or f"Jockey #{self.pk}"


# ============================================================
# CHEVAL
# ============================================================

class Cheval(ModeleHippisme):
    class Sexe(models.TextChoices):
        MALE = "MALE", "Mâle"
        FEMELLE = "FEMELLE", "Femelle"
        CASTRE = "CASTRE", "Hongre"
        INCONNU = "INCONNU", "Inconnu"

    numero_enregistrement = models.CharField(
        max_length=50,
        blank=True,
        db_index=True,
        verbose_name="Numéro d'enregistrement"
    )
    nom = models.CharField(
        max_length=150,
        db_index=True,
        verbose_name="Nom"
    )
    sexe = models.CharField(
        max_length=15,
        choices=Sexe.choices,
        default=Sexe.INCONNU,
        blank=True
    )
    date_naissance = models.DateField(
        null=True,
        blank=True
    )
    race = models.CharField(
        max_length=100,
        blank=True
    )
    couleur = models.CharField(
        max_length=50,
        blank=True
    )
    proprietaire = models.CharField(
        max_length=150,
        blank=True
    )
    entraineur_actuel = models.ForeignKey(
        Entraineur,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="chevaux",
        verbose_name="Entraîneur actuel"
    )
    observations = models.TextField(
        blank=True
    )
    est_actif = models.BooleanField(
        default=True,
        db_index=True
    )
    metadonnees = models.JSONField(
        default=dict,
        blank=True
    )

    class Meta:
        db_table = "chevaux"
        ordering = ["nom"]

    def __str__(self):
        return self.nom or f"Cheval #{self.pk}"


# ============================================================
# RÉUNION
# ============================================================

class Reunion(ModeleHippisme):
    class Statut(models.TextChoices):
        PROGRAMMEE = "PROGRAMMEE", "Programmée"
        EN_COURS = "EN_COURS", "En cours"
        TERMINEE = "TERMINEE", "Terminée"
        ANNULEE = "ANNULEE", "Annulée"
        REPORTEE = "REPORTEE", "Reportée"

    code = models.CharField(
        max_length=50,
        blank=True,
        db_index=True
    )
    numero = models.PositiveIntegerField(
        null=True,
        blank=True
    )
    nom = models.CharField(
        max_length=150,
        blank=True
    )
    hippodrome = models.ForeignKey(
        Hippodrome,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reunions",
        verbose_name="Hippodrome"
    )
    date_reunion = models.DateField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Date de réunion"
    )
    heure_debut = models.TimeField(
        null=True,
        blank=True
    )
    statut = models.CharField(
        max_length=20,
        choices=Statut.choices,
        default=Statut.PROGRAMMEE,
        blank=True,
        db_index=True
    )
    nombre_courses_prevu = models.PositiveIntegerField(
        default=0,
        blank=True
    )
    nombre_courses_terminees = models.PositiveIntegerField(
        default=0,
        blank=True
    )
    description = models.TextField(
        blank=True
    )
    metadonnees = models.JSONField(
        default=dict,
        blank=True
    )

    class Meta:
        db_table = "reunions"
        ordering = ["-id"]

    def __str__(self):
        if self.numero and self.date_reunion:
            return f"R{self.numero} - {self.date_reunion}"
        return self.nom or f"Réunion #{self.pk}"


# ============================================================
# COURSE
# ============================================================

class Course(ModeleHippisme):
    class Categorie(models.TextChoices):
        PLAT = "PLAT", "Plat"
        ATTELE = "ATTELE", "Attelé"
        MONTE = "MONTE", "Monté"
        OBSTACLE = "OBSTACLE", "Obstacle"
        AUTRE = "AUTRE", "Autre"

    class Statut(models.TextChoices):
        PROGRAMMEE = "PROGRAMMEE", "Programmée"
        OUVERTE = "OUVERTE", "Ouverte"
        EN_COURS = "EN_COURS", "En cours"
        TERMINEE = "TERMINEE", "Terminée"
        RESULTAT_PROVISOIRE = "RESULTAT_PROVISOIRE", "Résultat provisoire"
        RESULTAT_OFFICIEL = "RESULTAT_OFFICIEL", "Résultat officiel"
        ANNULEE = "ANNULEE", "Annulée"
        REPORTEE = "REPORTEE", "Reportée"

    reunion = models.ForeignKey(
        Reunion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="courses",
        verbose_name="Réunion"
    )
    numero = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Numéro de course"
    )
    code = models.CharField(
        max_length=50,
        blank=True,
        db_index=True
    )
    nom = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Nom"
    )
    categorie = models.CharField(
        max_length=20,
        choices=Categorie.choices,
        default=Categorie.PLAT,
        blank=True,
        db_index=True
    )
    distance_metres = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Distance en mètres"
    )
    nombre_partants_prevu = models.PositiveIntegerField(
        default=0,
        blank=True
    )
    heure_depart = models.TimeField(
        null=True,
        blank=True,
        verbose_name="Heure de départ prévue"
    )
    heure_depart_reelle = models.TimeField(
        null=True,
        blank=True,
        verbose_name="Heure de départ réelle"
    )
    statut = models.CharField(
        max_length=30,
        choices=Statut.choices,
        default=Statut.PROGRAMMEE,
        blank=True,
        db_index=True
    )
    est_active = models.BooleanField(
        default=True,
        db_index=True
    )
    conditions = models.TextField(
        blank=True
    )
    allocation = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True
    )
    commentaire = models.TextField(
        blank=True
    )
    metadonnees = models.JSONField(
        default=dict,
        blank=True
    )

    class Meta:
        db_table = "courses"
        ordering = ["-id"]

    def __str__(self):
        return f"Course {self.numero or ''} - {self.nom or self.pk}"


# ============================================================
# PARTANT
# ============================================================

class Partant(ModeleHippisme):
    course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="partants",
        verbose_name="Course"
    )
    cheval = models.ForeignKey(
        Cheval,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="participations",
        verbose_name="Cheval"
    )
    jockey = models.ForeignKey(
        Jockey,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="participations",
        verbose_name="Jockey"
    )
    entraineur = models.ForeignKey(
        Entraineur,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="participations",
        verbose_name="Entraîneur"
    )
    numero = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Numéro"
    )
    corde = models.PositiveIntegerField(
        null=True,
        blank=True
    )
    poids_kg = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    age = models.PositiveIntegerField(
        null=True,
        blank=True
    )
    cote = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True
    )
    est_non_partant = models.BooleanField(
        default=False,
        db_index=True
    )
    raison_non_partant = models.CharField(
        max_length=255,
        blank=True
    )
    observations = models.TextField(
        blank=True
    )
    donnees_source = models.JSONField(
        default=dict,
        blank=True
    )

    class Meta:
        db_table = "partants"
        ordering = ["-id"]

    def __str__(self):
        nom_cheval = self.cheval.nom if self.cheval else "Inconnu"
        return f"N°{self.numero or '?'} - {nom_cheval}"

    @property
    def identifiant_course(self):
        return self.course.code if self.course else None