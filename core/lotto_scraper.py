"""
Initialisierung core/lotto_scraper.py …
Ziel:

- HTML von lotto.de abrufen (statisch)
- Lottozahlen, Superzahl & Quoten extrahieren
- Rückgabe: Instanz von model.LottoZiehung
"""

import sys
import os

# 🔧 Fügt den Projekt-Hauptordner "Extracta/" zum Suchpfad hinzu
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


import requests
from bs4 import BeautifulSoup
from model.lotto_model import LottoZiehung
import datetime
import sys
import os


# Ziel-URL (offizielle Lottozahlen-Seite)
LOTTO_URL = "https://www.lotto.de/lotto-6aus49/lottozahlen"

def lade_html(url: str) -> str:
    """
    Führt einen einfachen GET-Request zur angegebenen URL aus.
    Gibt den HTML-Inhalt der Seite zurück (textbasiert).
    """
    response = requests.get(url)
    response.raise_for_status()  # Stoppt bei HTTP-Fehlern
    return response.text

def parse_lottoziehung(html: str) -> LottoZiehung:
    """
    Extrahiert Lottozahlen, Superzahl und Quoten aus dem HTML.
    Gibt eine fertige LottoZiehung-Instanz zurück.
    """
    soup = BeautifulSoup(html, "html.parser")

    #  Ziehungsdatum extrahieren (z. B. <time datetime="2025-04-10">)
    datum_tag = soup.find("time")
    datum = datum_tag["datetime"] if datum_tag else datetime.date.today().isoformat()

    #  Lottozahlen (6 aus 49)
    zahlen_tags = soup.select(".lotto-zahlen .zahl")[:6]  # Nur erste 6 Zahlen
    zahlen = [int(tag.text.strip()) for tag in zahlen_tags]

    #  Superzahl
    superzahl_tag = soup.select_one(".lotto-superzahl .zahl")
    superzahl = int(superzahl_tag.text.strip()) if superzahl_tag else -1

    #  Gewinnquoten (vereinfachte Darstellung)
    quoten = {}
    quoten_container = soup.select(".gewinnquoten .gewinnreihe")
    for zeile in quoten_container:
        klasse = zeile.select_one(".klasse").text.strip()
        betrag = zeile.select_one(".gewinnbetrag").text.strip()
        quoten[klasse] = betrag

    #  Rückgabe des Objekts
    return LottoZiehung(datum=datum, zahlen=zahlen, superzahl=superzahl, quoten=quoten)


def hole_aktuelle_ziehung() -> LottoZiehung:
    """
    Hauptfunktion: Ruft HTML von lotto.de ab und parst die Ziehung.
    Gibt eine LottoZiehung-Instanz zurück.
    """
    html = lade_html(LOTTO_URL)
    ziehung = parse_lottoziehung(html)
    return ziehung

# Testlauf (wird nur ausgeführt, wenn Datei direkt gestartet wird)
if __name__ == "__main__":
    html = lade_html(LOTTO_URL)

    # DEBUG: HTML anzeigen (die ersten 1000 Zeichen)
    soup = BeautifulSoup(html, "html.parser")
    print("\n🧪 HTML-Vorschau:")
    print(soup.prettify()[:1000])  # optional: auf 2000 erhöhen, wenn nötig

    # Dann Ziehung normal parsen und anzeigen
    ziehung = parse_lottoziehung(html)
    print("\n📦 Parsed Ziehung:")
    print(ziehung.to_dict())