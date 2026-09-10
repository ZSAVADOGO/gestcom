from django.urls import path

from .views import (
    HippismeAccueilView,
    HippodromeListView,
    HippodromeDetailView,
    HippodromeCreateView,
    HippodromeUpdateView,
    HippodromeDeleteView,
    EntraineurListView,
    EntraineurDetailView,
    EntraineurCreateView,
    EntraineurUpdateView,
    EntraineurDeleteView,
    JockeyListView,
    JockeyDetailView,
    JockeyCreateView,
    JockeyUpdateView,
    JockeyDeleteView,
    ChevalListView,
    ChevalDetailView,
    ChevalCreateView,
    ChevalUpdateView,
    ChevalDeleteView,
    ReunionListView,
    ReunionDetailView,
    ReunionCreateView,
    ReunionUpdateView,
    ReunionDeleteView,
    CourseListView,
    CourseDetailView,
    CourseCreateView,
    CourseUpdateView,
    CourseDeleteView,
    PartantListView,
    PartantDetailView,
    PartantCreateView,
    PartantUpdateView,
    PartantDeleteView,
)

app_name = "hippisme"


urlpatterns = [
    
    path("", HippismeAccueilView.as_view(), name="accueil"),
    # Hippodromes
    path("hippodromes/", HippodromeListView.as_view(), name="hippodromes"),
    path(
        "hippodromes/ajouter/", HippodromeCreateView.as_view(), name="hippodrome-creer"
    ),
    path(
        "hippodromes/<int:pk>/",
        HippodromeDetailView.as_view(),
        name="hippodrome-detail",
    ),
    path(
        "hippodromes/<int:pk>/modifier/",
        HippodromeUpdateView.as_view(),
        name="hippodrome-modifier",
    ),
    path(
        "hippodromes/<int:pk>/supprimer/",
        HippodromeDeleteView.as_view(),
        name="hippodrome-supprimer",
    ),
    # Entraîneurs
    path("entraineurs/", EntraineurListView.as_view(), name="entraineurs"),
    path(
        "entraineurs/ajouter/", EntraineurCreateView.as_view(), name="entraineur-creer"
    ),
    path(
        "entraineurs/<int:pk>/",
        EntraineurDetailView.as_view(),
        name="entraineur-detail",
    ),
    path(
        "entraineurs/<int:pk>/modifier/",
        EntraineurUpdateView.as_view(),
        name="entraineur-modifier",
    ),
    path(
        "entraineurs/<int:pk>/supprimer/",
        EntraineurDeleteView.as_view(),
        name="entraineur-supprimer",
    ),
    # Jockeys
    path("jockeys/", JockeyListView.as_view(), name="jockeys"),
    path("jockeys/ajouter/", JockeyCreateView.as_view(), name="jockey-creer"),
    path("jockeys/<int:pk>/", JockeyDetailView.as_view(), name="jockey-detail"),
    path(
        "jockeys/<int:pk>/modifier/", JockeyUpdateView.as_view(), name="jockey-modifier"
    ),
    path(
        "jockeys/<int:pk>/supprimer/",
        JockeyDeleteView.as_view(),
        name="jockey-supprimer",
    ),
    # Chevaux
    path("chevaux/", ChevalListView.as_view(), name="chevaux"),
    path("chevaux/ajouter/", ChevalCreateView.as_view(), name="cheval-creer"),
    path("chevaux/<int:pk>/", ChevalDetailView.as_view(), name="cheval-detail"),
    path(
        "chevaux/<int:pk>/modifier/", ChevalUpdateView.as_view(), name="cheval-modifier"
    ),
    path(
        "chevaux/<int:pk>/supprimer/",
        ChevalDeleteView.as_view(),
        name="cheval-supprimer",
    ),
    # Réunions
    path("reunions/", ReunionListView.as_view(), name="reunions"),
    path("reunions/ajouter/", ReunionCreateView.as_view(), name="reunion-creer"),
    path("reunions/<int:pk>/", ReunionDetailView.as_view(), name="reunion-detail"),
    path(
        "reunions/<int:pk>/modifier/",
        ReunionUpdateView.as_view(),
        name="reunion-modifier",
    ),
    path(
        "reunions/<int:pk>/supprimer/",
        ReunionDeleteView.as_view(),
        name="reunion-supprimer",
    ),
    # Courses
    path("courses/", CourseListView.as_view(), name="courses"),
    path("courses/ajouter/", CourseCreateView.as_view(), name="course-creer"),
    path("courses/<int:pk>/", CourseDetailView.as_view(), name="course-detail"),
    path(
        "courses/<int:pk>/modifier/", CourseUpdateView.as_view(), name="course-modifier"
    ),
    path(
        "courses/<int:pk>/supprimer/",
        CourseDeleteView.as_view(),
        name="course-supprimer",
    ),
    # Partants
    path("partants/", PartantListView.as_view(), name="partants"),
    path("partants/ajouter/", PartantCreateView.as_view(), name="partant-creer"),
    path("partants/<int:pk>/", PartantDetailView.as_view(), name="partant-detail"),
    path(
        "partants/<int:pk>/modifier/",
        PartantUpdateView.as_view(),
        name="partant-modifier",
    ),
    path(
        "partants/<int:pk>/supprimer/",
        PartantDeleteView.as_view(),
        name="partant-supprimer",
    ),
]
