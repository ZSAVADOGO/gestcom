"""
Étape "Découverte" du pipeline d'ingestion LONAB.

discover_result_pdfs() renvoie une liste de dict :
    [{"url": "...pdf", "label": "Télécharger les résultats PMU'B du 08 Septembre 2026"}, ...]

Chaque print() ci-dessous sert à visualiser, à l'exécution, ce que la fonction
est en train de faire ET ce qu'elle va retourner — utile en développement,
à retirer (ou remplacer par du logging) une fois en production.
"""

import time
import requests
from bs4 import BeautifulSoup

BASE = "https://www.lonab.bf/"
HEADERS = {"User-Agent": "TurfBF-DataBot/1.0 (contact: tech@votresociete.bf)"}


def discover_result_pdfs(max_pages: int = 5) -> list[dict]:
    """
    Parcourt les pages paginées de résultats LONAB et retourne la liste des
    PDF trouvés.

    Retour :
        list[dict] — une entrée par PDF trouvé, avec les clés "url" et "label".
        Liste vide si rien n'est trouvé (page inaccessible, gabarit HTML changé, etc.)
    """
    print(f"[discover_result_pdfs] Démarrage — jusqu'à {max_pages} page(s) à explorer")

    links: list[dict] = []

    for page in range(max_pages):
        url = f"{BASE}/resultats-gains-pmub"
        print(f"[discover_result_pdfs] → Requête page {page} : GET {url}?page={page}")

        try:
            resp = requests.get(url, params={"page": page}, headers=HEADERS, timeout=15)
            resp.raise_for_status()
        except requests.RequestException as exc:
            print(f"[discover_result_pdfs]   Échec de la requête sur la page {page} : {exc}")
            break

        print(f"[discover_result_pdfs]   Réponse reçue : statut {resp.status_code}, "
              f"{len(resp.content)} octets")

        soup = BeautifulSoup(resp.text, "html.parser")
        rows = soup.select("table a[href$='.pdf']")
        print(f"[discover_result_pdfs]   {len(rows)} lien(s) PDF détecté(s) sur cette page")

        if not rows:
            print(f"[discover_result_pdfs]   Aucun lien trouvé → on arrête la pagination ici")
            break

        for a in rows:
            href = a["href"]
            full_url = BASE + href if href.startswith("/") else href
            entry = {"url": full_url, "label": a.get_text(strip=True)}
            links.append(entry)
            print(f"[discover_result_pdfs]     + {entry}")

        time.sleep(2)  # politesse : pas de rafale de requêtes

    print(f"[discover_result_pdfs] Terminé — {len(links)} PDF au total collecté(s)")
    print(f"[discover_result_pdfs] Valeur retournée : {links!r}")

    return links


if __name__ == "__main__":
    # Exécution directe du fichier : python lonab_crawler.py
    result = discover_result_pdfs(max_pages=1)
    print("\n--- Résumé final ---")
    print(f"Type retourné : {type(result)}")
    print(f"Nombre d'éléments : {len(result)}")
    if result:
        print(f"Premier élément : {result[0]}")