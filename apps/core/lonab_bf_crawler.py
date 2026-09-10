import re
import time
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Optional


BASE = "https://www.lonab.bf"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) TurfBF-DataBot/1.0"
}

MOIS_FR = {
    "janvier": 1, "février": 2, "fevrier": 2, "mars": 3, "avril": 4,
    "mai": 5, "juin": 6, "juillet": 7, "août": 8, "aout": 8,
    "septembre": 9, "octobre": 10, "novembre": 11, "décembre": 12, "decembre": 12
}


def log(step: str, message: str, level: str = "INFO") -> None:
    symbols = {"INFO": "ℹ️", "SUCCESS": "✅", "WARN": "⚠️", "ERROR": "❌", "PROCESS": "⚙️"}
    print(f"[{symbols.get(level, '🔹')}] [{step}] {message}")


def parse_date_lonab(date_raw_str: str) -> tuple[Optional[str], Optional[str], Optional[datetime]]:
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


def parse_resultats_lonab(html_content: Optional[str] = None) -> Optional[dict]:
    if not html_content:
        url = f"{BASE}/"
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            resp.raise_for_status()
            html_content = resp.text
        except requests.RequestException as exc:
            log("ERROR", f"Échec lors du téléchargement HTML : {exc}", "ERROR")
            return None

    soup = BeautifulSoup(html_content, "html.parser")
    section = soup.find("section", id="block-resultats")

    if not section:
        log("PARSER", "Section '<section id=\"block-resultats\">' introuvable.", "WARN")
        return None

    log("PARSER", "Section des résultats identifiée.", "SUCCESS")
    text = section.get_text(" ", strip=True).replace("\xa0", " ")

    regex_titre_date = r"Résultats\s+du\s*[\"']?([^\"']+)[\"']?\s+du\s+([A-Za-zÀ-ÿ]+\s+\d{1,2}\s+[A-Za-zÀ-ÿ]+\s+\d{4})"
    date_match = re.search(regex_titre_date, text, re.IGNORECASE)

    titre_course = date_match.group(1).strip() if date_match else "4+1"
    full_date_str = date_match.group(2).strip() if date_match else ""

    jour_semaine, date_brute, dt_obj = parse_date_lonab(full_date_str)

    arrivee_match = re.search(r"ARR\s*:\s*([\d\s\-]+)", text)
    arrivee = (
        [n.strip() for n in arrivee_match.group(1).split("-") if n.strip()]
        if arrivee_match else []
    )

    np_match = re.search(r"NP\s*:\s*(\d+)", text)
    non_partants = np_match.group(1) if np_match else "00"

    rapports = {}
    items = section.select("ul li")
    for item in items:
        clean_item = item.get_text(strip=True).replace("\xa0", " ")
        if ":" in clean_item:
            partie_gauche, montant = clean_item.split(":", 1)
            libelle_match = re.search(r"(Ordre|Désordre|Bonus|C\s+Gagnant|C\s+Placé\s+[A-Z])", partie_gauche, re.IGNORECASE)
            libelle = libelle_match.group(1).strip() if libelle_match else partie_gauche.strip()

            montant_clean = re.sub(r"[^\d]", "", montant)
            if montant_clean:
                rapports[libelle] = int(montant_clean)

    print(f"DEBUG: titre_course={titre_course}, jour_semaine={jour_semaine}, date_brute={date_brute}, dt_obj={dt_obj}, arrivee={arrivee}, non_partants={non_partants}, rapports={rapports}")
    # Assurez-vous que date_dt soit une chaîne ISO serializable en JSON
    date_iso = dt_obj.isoformat() if dt_obj else None
    print(f"DEBUG: date_iso={date_iso}")  # DEBUG: Affiche la date au format ISO

    return {
        "titre": titre_course,
        "jour": jour_semaine,
        "date_str": date_brute or datetime.now().strftime("%d-%m-%Y"),
        "date_dt": date_iso,  # <-- FIX ICI: Chaîne ISO au lieu de l'objet datetime
        "arrivee": arrivee,
        "non_partants": non_partants,
        "rapports": rapports
    }
    """ return {
        "titre": titre_course,
        "jour": jour_semaine,
        "date_str": date_brute or datetime.now().strftime("%d-%m-%Y"),
        "date_dt": dt_obj,
        "arrivee": arrivee,
        "non_partants": non_partants,
        "rapports": rapports
    } """


def discover_result_pdfs(max_pages: int = 2) -> list[dict]:
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

        time.sleep(0.5)

    log("SUMMARY", f"{len(links)} PDF uniques identifiés.", "SUCCESS")
    return links


def run_lonab_collector(max_pdf_pages: int = 1) -> dict:
    log("SYSTEM", "LANCEMENT DE LA COLLECTE AUTOMATIQUE COMPLÈTE", "PROCESS")

    live_result = parse_resultats_lonab()
    pdfs = discover_result_pdfs(max_pages=max_pdf_pages)

    return {
        "resultat_direct": live_result,
        "liste_pdfs": pdfs
    }