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
>>> python core/ziehungs_historie_scraper.py

Output-Verzeichnisse:
- data/ziehungen_historie/ziehungen_YYYY.json
- data/ziehungen_historie/alle_ziehungen.csv
- data/ziehungen_historie/alle_ziehungen.xlsx
"""

import os
import json
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options

# Datenmodell der Ziehung
class LottoZiehung:
    def __init__(self, datum, jahr, zahlen, superzahl):
        self.datum = datum
        self.jahr = jahr
        self.zahlen = zahlen
        self.superzahl = superzahl

    def to_dict(self):
        return {
            "datum": self.datum,
            "jahr": self.jahr,
            "zahlen": self.zahlen,
            "superzahl": self.superzahl
        }

class LottoScraper:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        self.driver = webdriver.Chrome(service=ChromeService(), options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
        self.base_url = "https://www.lotto.de/lotto-6aus49/lottozahlen"
        self.output_dir = os.path.join("data", "ziehungen_historie")
        os.makedirs(self.output_dir, exist_ok=True)

    # Steuert die Auswahl eines Jahres im Dropdown-Menü
    def waehle_jahr(self, jahr):
        self.driver.get(self.base_url)
        self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "select")))
        selects = self.driver.find_elements(By.TAG_NAME, "select")
        for select in selects:
            options = select.find_elements(By.TAG_NAME, "option")
            for option in options:
                if option.text.strip() == str(jahr):
                    self.driver.execute_script(
                        "arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('change'));",
                        select, option.get_attribute("value")
                    )
                    time.sleep(2)
                    return

    # Wechselt auf eine bestimmte Ziehungsdatumsauswahl
    def lade_tag(self, value):
        selects = self.driver.find_elements(By.TAG_NAME, "select")
        for select in selects:
            if "Datum" in select.get_attribute("aria-label"):
                self.driver.execute_script(
                    "arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('change'));",
                    select, value
                )
                time.sleep(2)
                return

    # Extrahiert eine einzelne Ziehung mit Datum, Zahlen & Superzahl
    def extrahiere_ziehung(self, jahr, tag_option):
        try:
            datum = tag_option.text.strip()
            value = tag_option.get_attribute("value")
            self.lade_tag(value)

            self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".DrawNumbersCollection")))

            ziehungs_container = self.driver.find_elements(By.CSS_SELECTOR, ".DrawNumbersCollection__container")
            zahlen_spans = ziehungs_container[0].find_elements(By.CSS_SELECTOR, ".LottoBall__circle")
            zahlen = [int(z.get_attribute("aria-label")) for z in zahlen_spans[:6]]

            superzahl_spans = ziehungs_container[1].find_elements(By.CSS_SELECTOR, ".LottoBall__circle")
            superzahl = int(superzahl_spans[0].get_attribute("aria-label")) if superzahl_spans else None

            return LottoZiehung(datum, jahr, zahlen, superzahl).to_dict()
        except Exception as e:
            print(f"⚠️ Fehler bei Ziehung {jahr} {tag_option.text.strip()}: {e}")
            return None

    # Hauptlogik zur Extraktion aller Ziehungen eines Jahres
    def extrahiere_pro_jahr(self, jahr):
        self.waehle_jahr(jahr)
        time.sleep(2)

        ziehungen = []
        selects = self.driver.find_elements(By.TAG_NAME, "select")
        for select in selects:
            if "Datum" in select.get_attribute("aria-label"):
                optionen = select.find_elements(By.TAG_NAME, "option")
                for option in optionen:
                    ziehung = self.extrahiere_ziehung(jahr, option)
                    if ziehung:
                        ziehungen.append(ziehung)
                break

        return ziehungen

    # Speichert Ziehungen eines Jahres als JSON
    def speichere_json(self, jahr, ziehungen):
        pfad = os.path.join(self.output_dir, f"ziehungen_{jahr}.json")
        with open(pfad, "w", encoding="utf-8") as f:
            json.dump(ziehungen, f, indent=2, ensure_ascii=False)
        print(f" Gespeichert: {pfad}")

    # Exportiert alles als CSV & Excel
    def exportiere_gesamt(self):
        alle = []
        for fname in os.listdir(self.output_dir):
            if fname.endswith(".json") and fname.startswith("ziehungen_"):
                with open(os.path.join(self.output_dir, fname), "r", encoding="utf-8") as f:
                    alle.extend(json.load(f))

        if not alle:
            print(" Keine Daten für Export gefunden.")
            return

        df = pd.DataFrame(alle)
        df.to_csv(os.path.join(self.output_dir, "alle_ziehungen.csv"), index=False)
        df.to_excel(os.path.join(self.output_dir, "alle_ziehungen.xlsx"), index=False)
        print("📄 Export abgeschlossen (CSV + Excel)")

    # Steuerung des gesamten Ablaufs über Jahre hinweg
    def scrape(self, start_jahr=1955, end_jahr=2025):
        for jahr in range(start_jahr, end_jahr + 1):
            print(f"Jahr {jahr} wird bearbeitet...")
            ziehungen = self.extrahiere_pro_jahr(jahr)
            self.speichere_json(jahr, ziehungen)
        self.exportiere_gesamt()

    def beenden(self):
        self.driver.quit()

# Startpunkt des Programms
if __name__ == "__main__":
    scraper = LottoScraper()
    scraper.scrape(1955, 2025)
    scraper.beenden()
