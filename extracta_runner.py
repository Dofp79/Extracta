"""
Initialisierung extracta_runner.py …
Ziel:

- Startet den Scraper (core/lotto_scraper.py)
- Prüft, ob die Ziehung bereits existiert
- Speichert neue Ziehungen über model/lotto_model.py
- Gibt Informationen im Terminal aus

Benötigt:
✔️ core/lotto_scraper.py
✔️ model/lotto_model.py
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.lotto_scraper import hole_aktuelle_ziehung
from model.lotto_model import lade_bestehende_ziehungen, ist_neue_ziehung, speichere_ziehung

def main():
    print(" Starte Extracta…")

    try:
        #  Schritt 1: Aktuelle Ziehung holen
        ziehung = hole_aktuelle_ziehung()
        print(f" Ziehungsdatum: {ziehung.datum}")
        print(f" Zahlen: {ziehung.zahlen} + Superzahl: {ziehung.superzahl}")
        
        #  Schritt 2: Bestehende Daten laden
        bestehende = lade_bestehende_ziehungen()

        #  Schritt 3: Prüfen, ob die Ziehung neu ist
        if ist_neue_ziehung(ziehung, bestehende):
            print(" Neue Ziehung erkannt – wird gespeichert…")
            speichere_ziehung(ziehung)
        else:
            print(" Ziehung bereits vorhanden – keine Aktion erforderlich.")

    except Exception as e:
        print(" FEHLER beim Ausführen von Extracta:")
        print(e)

if __name__ == "__main__":
    main()
