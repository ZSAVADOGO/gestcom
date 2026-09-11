from django.test import TestCase, Client
from django.urls import reverse
from .models import PointVente


class PointVenteTests(TestCase):

    def setUp(self):
        """Initialisation des données de test avant chaque test."""
        self.client = Client()
        self.pv_actif = PointVente.objects.create(
            code="PV001",
            nom="Agence Centre",
            type="AGENCE",
            ville="Ouagadougou",
            quartier="Koulouba",
            telephone="70000001",
            est_actif=True,
            est_principal=True,
        )
        self.pv_inactif = PointVente.objects.create(
            code="PV002",
            nom="Kiosque Sud",
            type="POINT_VENTE",
            ville="Bobo-Dioulasso",
            quartier="Sarra",
            telephone="70000002",
            est_actif=False,
            est_principal=False,
        )

    # --- 1. TESTS DE L'API DE LISTAGE ET FILTRES ---

    def test_api_lister_points_vente(self):
        """Vérifie que l'API renvoie la liste et la structure de pagination."""
        url = reverse("points_vente:api_lister_point_vente")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(json_data["status"], "success")
        self.assertIn("pagination", json_data)
        self.assertEqual(json_data["pagination"]["total_elements"], 2)

    def test_filtre_par_statut_actif(self):
        """Vérifie que le filtre statut=actif ne renvoie que les PV actifs."""
        url = reverse("points_vente:api_lister_point_vente")
        response = self.client.get(url, {"statut": "actif"})

        json_data = response.json()
        self.assertEqual(len(json_data["objects"]), 1)
        self.assertEqual(json_data["objects"][0]["code"], "PV001")

    def test_filtre_par_statut_inactif(self):
        """Vérifie que le filtre statut=inactif ne renvoie que les PV inactifs."""
        url = reverse("points_vente:api_lister_point_vente")
        response = self.client.get(url, {"statut": "inactif"})

        json_data = response.json()
        self.assertEqual(len(json_data["objects"]), 1)
        self.assertEqual(json_data["objects"][0]["code"], "PV002")


    def test_recherche_par_mot_cle(self):
        """Vérifie le fonctionnement de la barre de recherche par nom et code."""
        url = reverse("points_vente:api_lister_point_vente")

        # 1. Test de recherche par NOM ("Kiosque")
        response_nom = self.client.get(url, {"q": "Kiosque"})
        self.assertEqual(response_nom.status_code, 200)
        data_nom = response_nom.json()
        self.assertEqual(len(data_nom["objects"]), 1)
        self.assertEqual(data_nom["objects"][0]["nom"], "Kiosque Sud")

        # 2. Test de recherche par CODE ("PV001")
        response_code = self.client.get(url, {"q": "PV001"})
        self.assertEqual(response_code.status_code, 200)
        data_code = response_code.json()
        self.assertEqual(len(data_code["objects"]), 1)
        self.assertEqual(data_code["objects"][0]["code"], "PV001")


    # --- 2. TESTS DE CRÉATION (POST) ---

    def test_creer_point_vente_succes(self):
        """Vérifie la création valide d'un point de vente."""
        url = reverse("points_vente:creer_point_vente")
        payload = {
            "code": "PV003",
            "nom": "Nouveau Kiosque",
            "type": "POINT_VENTE",
            "ville": "Ouagadougou",
            "est_actif": "true",
        }
        response = self.client.post(url, payload)

        self.assertEqual(response.status_code, 201)
        self.assertTrue(PointVente.objects.filter(code="PV003").exists())

    def test_creer_point_vente_code_doublon_erreur(self):
        """Vérifie le rejet d'un code déjà existant."""
        url = reverse("points_vente:creer_point_vente")
        payload = {
            "code": "PV001",  # Déjà créé dans setUp
            "nom": "Tentative Doublon",
            "type": "POINT_VENTE",
            "ville": "Ouagadougou",
        }
        response = self.client.post(url, payload)

        self.assertEqual(response.status_code, 400)
        json_data = response.json()
        self.assertIn("erreur", json_data)

    # --- 3. TESTS DE MODIFICATION (POST) ---

    def test_modifier_point_vente_succes(self):
        """Vérifie la mise à jour d'un point de vente existant."""
        url = reverse("points_vente:modifier_point_vente", kwargs={"point_vente_id": self.pv_actif.id})
        payload = {
            "code": "PV001",
            "nom": "Agence Centre Modifiée",
            "type": "AGENCE",
            "ville": "Ouagadougou",
            "est_actif": "true",
        }
        response = self.client.post(url, payload)

        self.assertEqual(response.status_code, 200)
        self.pv_actif.refresh_from_db()
        self.assertEqual(self.pv_actif.nom, "Agence Centre Modifiée")

    def test_modifier_point_vente_inexistant_404(self):
        """Vérifie qu'une tentative sur un ID inconnu renvoie 404."""
        url = reverse("points_vente:modifier_point_vente", kwargs={"point_vente_id": 9999})
        payload = {
            "code": "PV999",
            "nom": "Fantôme",
            "type": "AGENCE",
            "ville": "Ouagadougou",
        }
        response = self.client.post(url, payload)

        self.assertEqual(response.status_code, 404)