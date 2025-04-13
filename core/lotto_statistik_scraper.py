"""
Scraper für die Lottozahlen-Ziehungshäufigkeit
Zielseite: https://www.lotto.de/lotto-6aus49/statistik/ziehungshaeufigkeit
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Tuple
from core.haeufigkeit_speicher import HaeufigkeitSpeicher

# URL der Statistikseite
STATISTIK_URL = "https://www.lotto.de/lotto-6aus49/statistik/ziehungshaeufigkeit"

def lade_html(url: str) -> str:
    """
    Lädt das HTML der angegebenen URL per GET-Request.
    Zusätzlich wird das HTML in einer Datei gespeichert zur Analyse.
    """
    response = requests.get(url)
    response.raise_for_status()
    html = response.text

    # SPEICHERUNG ZUR DIAGNOSE
    with open("debug_statistik.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(" HTML gespeichert als debug_statistik.html")

    return html

def parse_haeufigkeiten(html: str) -> dict:
    """
    Parst die Ziehungshäufigkeiten aus dem HTML und gibt sie als Dictionary zurück.
    """
    soup = BeautifulSoup(html, "html.parser")
    bars = soup.select(".StatisticsBar")
    if not bars:
        raise ValueError("⚠️ Keine Statistik-Bars gefunden – Selector eventuell falsch.")

    daten = {}
    for bar in bars:
        try:
            zahl_tag = bar.select_one(".LottoBall__circle")
            zahl = int(zahl_tag["aria-label"].strip())

            count_tag = bar.select_one(".StatisticsBar__count")
            haeufigkeit = int(count_tag.text.replace("×", "").strip())

            daten[zahl] = haeufigkeit
        except Exception as e:
            print(f"Fehler beim Parsen eines Eintrags: {e}")
            continue

    return daten

# Testlauf
if __name__ == "__main__":
    html = lade_html(STATISTIK_URL)
    daten = parse_haeufigkeiten(html)

    print("🎱 Häufigkeiten:")
    for zahl in sorted(daten):
        print(f"Zahl {zahl:>2}: {daten[zahl]}x")

    # Speichern in Formate
    speicher = HaeufigkeitSpeicher()
    speicher.speichere_json(daten)
    speicher.speichere_csv(daten)
    speicher.speichere_excel(daten)
