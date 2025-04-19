"""
Modulname: ziehungs_historie_scraper.py
Pfad:     core/ziehungs_historie_scraper.py
Autor:    Cody | GPT-gestützter Lotto-Datenscraper
Zweck:    Automatischer Scraper für alle Ziehungen des Spiels „Lotto 6 aus 49“ von 1955 bis heute
Website:  https://www.lotto.de/lotto-6aus49/lottozahlen

Funktionen:
- Steuert Jahr- & Datumsauswahl dynamisch über die Weboberfläche
- Extrahiert Ziehungsdaten (Datum, 6 Zahlen, Superzahl)
- Speichert pro Jahr als JSON-Datei
- Erstellt zusammenfassende CSV- und Excel-Dateien für alle Ziehungen

Abhängigkeiten:
- Selenium
- pandas
- openpyxl

Nutzung:

>>> PS C:\Extracta> .\venv\Scripts\activate
>>> (venv) PS C:\Extracta> python core/ziehungs_historie_scraper.py
>>> python core/ziehungs_historie_scraper.py
"""

import os
import time
import json
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Zielseite, von der gescrapt wird
BASE_URL = "https://www.lotto.de/lotto-6aus49/lottozahlen"
DATA_PATH = os.path.join("data", "ziehungen_historie")
os.makedirs(DATA_PATH, exist_ok=True)

class LottoScraper:
    def __init__(self):
        """
        Initialisiert den Chrome WebDriver im Headless-Modus (unsichtbarer Browser).
        """
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        self.driver = webdriver.Chrome(service=Service("tools/chromedriver.exe"), options=chrome_options)

    def lade_jahr_und_tag(self, jahr, tag_value):
        """
        Öffnet die Website und wählt ein bestimmtes Jahr und einen Ziehungstag aus.
        Dies wird über JavaScript ausgelöst (wie ein echter Klick).
        """
        self.driver.get(BASE_URL)
        time.sleep(2)

        jahr_select = self.driver.find_element(By.CSS_SELECTOR, "select[id^='selectedYear-select']")
        self.driver.execute_script(
            "arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('change'));",
            jahr_select, str(jahr)
        )
        time.sleep(2)

        tag_select = self.driver.find_element(By.CSS_SELECTOR, "select[id^='daySelect-select']")
        self.driver.execute_script(
            "arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('change'));",
            tag_select, tag_value
        )
        time.sleep(2)

    def extrahiere_daten(self, jahr, datum):
        """
        Wartet auf die Lottozahlen (6 Kugeln) und Superzahl.
        Gibt ein Dictionary mit Datum, Jahr, Zahlen und Superzahl zurück.
        """
        try:
            #  Warten bis 6 Kugeln im DOM erscheinen
            WebDriverWait(self.driver, 10).until(
                lambda d: len(
                    d.find_elements(By.CSS_SELECTOR, ".DrawNumbersCollection__container")[0]
                    .find_elements(By.CLASS_NAME, "LottoBall")
                ) >= 6
            )

            # Lottozahlen extrahieren
            zahlen_container = self.driver.find_elements(By.CSS_SELECTOR, ".DrawNumbersCollection__container")[0]
            zahlen_elems = zahlen_container.find_elements(By.CLASS_NAME, "LottoBall")
            zahlen = [int(el.text.strip()) for el in zahlen_elems]

        except Exception as e:
            print(f" Lottozahlen fehlen für {datum} ({jahr}): {e}")
            zahlen = []

        try:
            #  Superzahl warten und extrahieren
            WebDriverWait(self.driver, 5).until(
                lambda d: d.find_elements(By.CSS_SELECTOR, ".DrawNumbersCollection__container")[1]
                .find_element(By.CLASS_NAME, "LottoBall")
            )

            super_container = self.driver.find_elements(By.CSS_SELECTOR, ".DrawNumbersCollection__container")[1]
            super_elem = super_container.find_element(By.CLASS_NAME, "LottoBall")
            superzahl = int(super_elem.text.strip())

        except Exception as e:
            print(f" Superzahl fehlt für {datum} ({jahr}): {e}")
            superzahl = None

        return {
            "datum": datum,
            "jahr": jahr,
            "zahlen": zahlen,
            "superzahl": superzahl
        }

    def extrahiere_pro_jahr(self, jahr):
        """
        Für ein bestimmtes Jahr:
        1. Lade alle Datum-Optionen
        2. Iteriere durch alle Ziehungen
        3. Extrahiere und speichere die Daten in einer JSON-Datei
        """
        print(f" Jahr {jahr} wird verarbeitet …")
        self.driver.get(BASE_URL)
        time.sleep(2)

        jahr_select = self.driver.find_element(By.CSS_SELECTOR, "select[id^='selectedYear-select']")
        self.driver.execute_script(
            "arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('change'));",
            jahr_select, str(jahr)
        )
        time.sleep(2)

        # Warte und hole die Optionen für alle Ziehungstage
        for _ in range(10):
            try:
                tag_select = self.driver.find_element(By.CSS_SELECTOR, "select[id^='daySelect-select']")
                optionen = tag_select.find_elements(By.TAG_NAME, "option")
                break
            except Exception:
                time.sleep(1)
        else:
            print(f"Konnte Tage für Jahr {jahr} nicht laden.")
            return []

        # Wichtig: jedes Mal neu selektieren, da Seite neu rendert
        anzahl_optionen = len(optionen)
        ziehungen = []

        for i in range(anzahl_optionen):
            try:
                # Dropdown neu holen, da es sich nach jeder Interaktion aktualisiert
                tag_select = self.driver.find_element(By.CSS_SELECTOR, "select[id^='daySelect-select']")
                option = tag_select.find_elements(By.TAG_NAME, "option")[i]

                tag_value = option.get_attribute("value")
                datum = option.text.strip()

                self.lade_jahr_und_tag(jahr, tag_value)
                daten = self.extrahiere_daten(jahr, datum)
                ziehungen.append(daten)

            except Exception as e:
                print(f" Fehler bei Ziehung: Index {i}, Jahr {jahr} – {e}")

        # Speichern als JSON
        with open(os.path.join(DATA_PATH, f"ziehungen_{jahr}.json"), "w", encoding="utf-8") as f:
            json.dump(ziehungen, f, ensure_ascii=False, indent=2)

        return ziehungen

    def scrape(self, start=1955, ende=2025):
        """
        Hauptfunktion für den Vollscan: Alle Ziehungen aller Jahre scrapen.
        - Pro Jahr als JSON speichern
        - Gesamtausgabe als CSV + Excel
        """
        alle_ziehungen = []
        for jahr in range(start, ende + 1):
            ziehungen = self.extrahiere_pro_jahr(jahr)
            alle_ziehungen.extend(ziehungen)

        df = pd.DataFrame(alle_ziehungen)
        df.to_csv(os.path.join(DATA_PATH, "alle_ziehungen.csv"), index=False)
        df.to_excel(os.path.join(DATA_PATH, "alle_ziehungen.xlsx"), index=False)

        print(f"✅ Export abgeschlossen: {len(alle_ziehungen)} Ziehungen gespeichert.")

    def beenden(self):
        """Beendet die Browser-Sitzung korrekt."""
        self.driver.quit()


# ========== Haupteinstiegspunkt für CLI-Start ==========
if __name__ == "__main__":
    scraper = LottoScraper()
    scraper.scrape(start=1955, ende=1956)  # Testjahr, z. B. 1969 → ganze Serie 1955–2025
    scraper.beenden()
