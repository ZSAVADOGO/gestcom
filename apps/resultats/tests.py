from django.test import TestCase, Client
from django.urls import reverse
from .models import Resultat


class ResultatTests(TestCase):

    def setUp(self):
        self.client = Client()

        self.res1 = Resultat.objects.create(
            statut=Resultat.Statut.OFFICIEL,
            non_partants="02",
            source="Scraper LONAB",
            commentaire="Course rapide"
        )
        self.res1.set_arrivee_depuis_liste(["14", "3", "5"])
        self.res1.save()

        self.res2 = Resultat.objects.create(
            statut=Resultat.Statut.PROVISOIRE,
            non_partants="00",
            source="Manual Entry",
            commentaire="En attente confirmation"
        )
        self.res2.set_arrivee_depuis_liste(["1", "2", "3"])
        self.res2.save()

    def test_api_lister_resultats(self):
        url = reverse("resultats:api_lister_resultats")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(len(data["objects"]), 2)

    def test_recherche_par_mot_cle(self):
        url = reverse("resultats:api_lister_resultats")

        # Recherche par source ("LONAB")
        response = self.client.get(url, {"q": "LONAB"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["objects"]), 1)
        self.assertEqual(data["objects"][0]["source"], "Scraper LONAB")

    def test_filtre_statut(self):
        url = reverse("resultats:api_lister_resultats")

        response = self.client.get(url, {"statut": "OFFICIEL"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["objects"]), 1)
        self.assertEqual(data["objects"][0]["statut"], "OFFICIEL")