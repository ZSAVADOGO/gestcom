import re
import time
from datetime import datetime
from typing import Optional, TypedDict
import requests
from bs4 import BeautifulSoup

import json

BASE = "https://www.lonab.bf"
HEADERS = {
    "User-Agent": "TurfBF-DataBot/1.0 (contact: tech@votresociete.bf)"
}

MOIS_FR = {
    "janvier": 1, "février": 2, "fevrier": 2, "mars": 3, "avril": 4,
    "mai": 5, "juin": 6, "juillet": 7, "août": 8, "aout": 8,
    "septembre": 9, "octobre": 10, "novembre": 11, "décembre": 12, "decembre": 12
}


def log(step: str, message: str, level: str = "INFO") -> None:
    """Formatte les sorties console pour un suivi visuel clair."""
    symbols = {"INFO": "ℹ️", "SUCCESS": "✅", "WARN": "⚠️", "ERROR": "❌", "PROCESS": "⚙️"}
    print(f"[{symbols.get(level, '🔹')}] [{step}] {message}")


def parse_date_lonab(date_raw_str: str) -> tuple[Optional[str], Optional[str], Optional[datetime]]:
    """Extrait le jour, la date brute et convertit en datetime Python."""
    pattern = r"(?P<jour>[A-Za-zÀ-ÿ]+)\s+(?P<jour_num>\d{1,2})\s+(?P<mois>[A-Za-zÀ-ÿ]+)\s+(?P<annee>\d{4})"
    match = re.search(pattern, date_raw_str)

    if not match:
        return None, None, None

    jour_semaine = match.group("jour").capitalize()
    jour_num = int(match.group("jour_num"))
    mois_nom = match.group("mois").lower()
    annee = int(match.group("annee"))

    date_brute = f"{jour_num:02d} {match.group('mois').capitalize()} {annee}"
    mois_num = MOIS_FR.get(mois_nom)
    dt_obj = datetime(annee, mois_num, jour_num) if mois_num else None

    return jour_semaine, date_brute, dt_obj


#def parse_resultats_lonab(html_content: str) -> Optional[dict]:
def parse_resultats_lonab(html_content: str = None) -> dict:
    """Parse le bloc HTML <section id="block-resultats">."""
    
    """
    Analyse le contenu HTML des résultats LONAB.
    Si html_content n'est pas fourni, effectue la requête automatiquement.
    """
    if html_content is None:
        #url = "https://www.lonab.bf/resultats"
        url = "https://www.lonab.bf"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers, timeout=15)
        html_content = response.text
    
    soup = BeautifulSoup(html_content, "html.parser")
    section = soup.find("section", id="block-resultats")

    if not section:
        log("PARSER", "Section '<section id=\"block-resultats\">' introuvable.", "WARN")
        return None

    log("PARSER", "Section des résultats identifiée.", "SUCCESS")
    text = section.get_text(" ", strip=True).replace("\xa0", " ")

    # 1. Extraction Titre, Jour et Date
    regex_titre_date = r"Résultats\s+du\s*[\"']?([^\"']+)[\"']?\s+du\s+([A-Za-zÀ-ÿ]+\s+\d{1,2}\s+[A-Za-zÀ-ÿ]+\s+\d{4})"
    date_match = re.search(regex_titre_date, text, re.IGNORECASE)

    titre_course = date_match.group(1).strip() if date_match else "4+1"
    full_date_str = date_match.group(2).strip() if date_match else ""

    jour_semaine, date_brute, dt_obj = parse_date_lonab(full_date_str)

    # 2. Extraction Arrivée
    arrivee_match = re.search(r"ARR\s*:\s*([\d\s\-]+)", text)
    arrivee = (
        [n.strip() for n in arrivee_match.group(1).split("-") if n.strip()]
        if arrivee_match else []
    )

    # 3. Non-partants
    np_match = re.search(r"NP\s*:\s*(\d+)", text)
    non_partants = np_match.group(1) if np_match else "00"

    # 4. Rapports (Gains) avec nettoyage des bruits/mots parasite
    rapports = {}
    items = section.select("ul li")
    for item in items:
        clean_item = item.get_text(strip=True).replace("\xa0", " ")
        if ":" in clean_item:
            partie_gauche, montant = clean_item.split(":", 1)
            # Nettoyage pour ne garder que l'intitulé du pari (ex: 'Ordre', 'Désordre', 'Bonus')
            libelle_match = re.search(r"(Ordre|Désordre|Bonus|C\s+Gagnant|C\s+Placé\s+[A-Z])", partie_gauche, re.IGNORECASE)
            libelle = libelle_match.group(1).strip() if libelle_match else partie_gauche.strip()

            montant_clean = re.sub(r"[^\d]", "", montant)
            if montant_clean:
                rapports[libelle] = int(montant_clean)

    return {
        "titre": titre_course,
        "jour": jour_semaine,
        "date_str": date_brute,
        "date_dt": dt_obj,
        "arrivee": arrivee,
        "non_partants": non_partants,
        "rapports": rapports
    }


def fetch_live_resultats() -> Optional[dict]:
    """Récupère automatiquement le HTML en direct de la page d'accueil et extrait les résultats."""
    url = f"{BASE}/"
    log("HTTP", f"Récupération en direct des résultats sur {url}", "PROCESS")
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        log("HTTP", "Page d'accueil chargée avec succès.", "SUCCESS")
        return parse_resultats_lonab(resp.text)
    except requests.RequestException as exc:
        log("ERROR", f"Échec lors de la récupération directe : {exc}", "ERROR")
        return None


def discover_result_pdfs(max_pages: int = 5) -> list[dict]:
    """Parcourt les pages paginées des résultats pour extraire tous les liens PDF."""
    log("INIT", f"Découverte des PDF (jusqu'à {max_pages} pages)", "PROCESS")
    links: list[dict] = []
    seen_urls: set[str] = set()

    for page in range(max_pages):
        url = f"{BASE}/resultats-gains-pmub"
        try:
            resp = requests.get(url, params={"page": page}, headers=HEADERS, timeout=15)
            resp.raise_for_status()
        except requests.RequestException as exc:
            log("ERROR", f"Échec de la requête sur la page {page} : {exc}", "ERROR")
            break

        soup = BeautifulSoup(resp.text, "html.parser")
        rows = soup.select("table a[href$='.pdf']")

        if not rows:
            log("WARN", f"Aucun PDF sur la page {page}. Arrêt de la pagination.", "WARN")
            break

        for a in rows:
            href = a.get("href", "").strip()
            if not href:
                continue
            full_url = BASE + href if href.startswith("/") else href
            label = a.get_text(strip=True)

            if full_url not in seen_urls:
                seen_urls.add(full_url)
                links.append({"url": full_url, "label": label})

        time.sleep(1)

    log("SUMMARY", f"{len(links)} PDF uniques identifiés.", "SUCCESS")
    return links


def run_lonab_collector(max_pdf_pages: int = 2) -> dict:
    """Lance la collecte automatique complète (PDFs + Résultats HTML direct)."""
    print("\n" + "=" * 60)
    log("SYSTEM", "LANCEMENT DE LA COLLECTE AUTOMATIQUE COMPLÈTE", "PROCESS")
    print("=" * 60)

    live_result = fetch_live_resultats()
    pdfs = discover_result_pdfs(max_pages=max_pdf_pages)

    return {
        "resultat_direct": live_result,
        "liste_pdfs": pdfs
    }


# ==============================================================================
# EXECUTION SCRIPT
# ==============================================================================

if __name__ == "__main__":
    # Exécution globale automatique
    data_collectees = run_lonab_collector(max_pdf_pages=2)

    print("\n" + "="*50)
    print("        --- RÉSUMÉ DES DONNÉES EXTRAITES ---")
    print("="*50)
    
    # Formatage propre du dictionnaire (gère le datetime grâce à default=str)
    res_direct_clean = json.dumps(data_collectees["resultat_direct"], indent=4, ensure_ascii=False, default=str)
    print(f"\n1. 🛑 Dernier Résultat en Direct :\n{res_direct_clean}")
    
    print(f"\n2. 📄 Nombre de PDF trouvés : {len(data_collectees['liste_pdfs'])}")
    if data_collectees["liste_pdfs"]:
        pdf_clean = json.dumps(data_collectees["liste_pdfs"][0], indent=4, ensure_ascii=False)
        print(f"   🔹 Exemple du premier PDF :\n{pdf_clean}")
    print("\n" + "="*50)