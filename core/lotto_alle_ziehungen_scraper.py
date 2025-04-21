"""
Modulname: lotto_alle_ziehungen_scraper.py
Pfad:     core/lotto_alle_ziehungen_scraper.py
Zweck:    Vollständiger & robuster Web-Scraper für alle Ziehungen des Spiels „Lotto 6 aus 49“ von 1955 bis heute.
Website:  https://www.lotto.de/lotto-6aus49/lottozahlen

Beschreibung:
Dieses Skript automatisiert den Abruf aller historischen Lottoziehungen vom offiziellen Lotto-Portal.
Es navigiert die Auswahlmenüs für Jahr und Ziehungsdatum dynamisch und extrahiert für jede Ziehung:
- Datum
- Jahr
- 6 gezogene Lottozahlen
- Superzahl

Funktionen:
- Navigiert durch die Jahres- und Datumsauswahl
- Erkennt DOM-Änderungen und wartet aktiv auf neue Ziehungsdaten
- Extrahiert vollständige Ziehungsdaten je Datum
- Implementiert Retry-Logik bei fehlerhaften DOM-Zugriffen
- Ignoriert leere oder fehlerhafte Dropdown-Einträge
- Optional: sichtbarer Browser für Tests (Headless kann deaktiviert werden)
- Exportiert Daten in Excel-Datei
- Fehlerhafte Ziehungen werden separat protokolliert (JSON)

Abhängigkeiten:
- Selenium
- pandas
- openpyxl

Verwendung:
>>> (venv) PS E:\Extracta> python core/lotto_alle_ziehungen_scraper.py
"""


import os
import time
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = "https://www.lotto.de/lotto-6aus49/lottozahlen"
DATA_PATH = "data"
os.makedirs(DATA_PATH, exist_ok=True)

class LottoScraper:
    # Initialisiert den Selenium WebDriver (Chrome, Headless) und erstellt eine Fehlerliste.
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(service=Service("tools/chromedriver.exe"), options=chrome_options)
        self.fehlerhafte_ziehungen = []

    # Wählt ein bestimmtes Jahr und Ziehungstag im Dropdown aus und wartet auf neue Ziehungsdaten.
    def lade_jahr_und_tag(self, jahr, tag_value):
        self.driver.get(BASE_URL)
        time.sleep(2)

        jahr_select = Select(self.driver.find_element(By.CSS_SELECTOR, "select[id^='selectedYear-select']"))
        jahr_select.select_by_value(str(jahr))
        time.sleep(1)

        tag_select = Select(self.driver.find_element(By.CSS_SELECTOR, "select[id^='daySelect-select']"))
        tag_select.select_by_value(tag_value)

        try:
            alte_zahl = self.driver.find_elements(By.CSS_SELECTOR, ".DrawNumbersCollection__container")[0]\
                         .find_elements(By.CLASS_NAME, "LottoBall")[0].text.strip()
        except:
            alte_zahl = ""

        # Wird verwendet, um einen DOM-Wechsel zu erkennen, also: Ist die neu geladene Zahl im DOM anders als die alte?
        def neue_zahl_geladen(driver):
            try:
                neue_zahl = driver.find_elements(By.CSS_SELECTOR, ".DrawNumbersCollection__container")[0]\
                              .find_elements(By.CLASS_NAME, "LottoBall")[0].text.strip()
                return neue_zahl != "" and neue_zahl != alte_zahl
            except:
                return False

        WebDriverWait(self.driver, 10).until(neue_zahl_geladen)
        time.sleep(0.5)

    # Extrahiert die 6 Lottozahlen und die Superzahl von der aktuellen Seite.
    def extrahiere_daten(self, jahr, datum):
        try:
            container = self.driver.find_elements(By.CSS_SELECTOR, ".DrawNumbersCollection__container")
            zahlen = [int(el.text.strip()) for el in container[0].find_elements(By.CLASS_NAME, "LottoBall")]
            superzahl = int(container[1].find_element(By.CLASS_NAME, "LottoBall").text.strip()) if len(container) > 1 else None
        except:
            zahlen = []
            superzahl = None
        return {
            "datum": datum,
            "jahr": jahr,
            "zahl_1": zahlen[0] if len(zahlen) > 0 else None,
            "zahl_2": zahlen[1] if len(zahlen) > 1 else None,
            "zahl_3": zahlen[2] if len(zahlen) > 2 else None,
            "zahl_4": zahlen[3] if len(zahlen) > 3 else None,
            "zahl_5": zahlen[4] if len(zahlen) > 4 else None,
            "zahl_6": zahlen[5] if len(zahlen) > 5 else None,
            "superzahl": superzahl
        }
    """
    Diese Methode ist das Haupt-Scraping-Verfahren,  Iteriert über alle Jahre und Ziehungen, extrahiert die Daten, implementiert Retry-Logik:
    - durch alle Jahre iteriert (1955–2025)
    - für jedes Jahr alle Ziehungsdaten-Tage auswählt
    - die Lottozahlen und Superzahl extrahiert
    - die Daten speichert (oder Fehler dokumentiert)
    """
    def extrahiere_alle_daten(self, start=1955, ende=2025):
        daten = [] # Initialisierung der Ergebnisliste
        for jahr in range(start, ende + 1):
            print(f"🔄 Verarbeite Jahr {jahr} …")
            self.driver.get(BASE_URL)
            time.sleep(2)

            # Öffnet die Lotto-Seite und wählt das aktuelle Jahr im Dropdown-Menü
            jahr_select = Select(self.driver.find_element(By.CSS_SELECTOR, "select[id^='selectedYear-select']"))
            jahr_select.select_by_value(str(jahr))
            time.sleep(2)

            try:
                tag_select = Select(self.driver.find_element(By.CSS_SELECTOR, "select[id^='daySelect-select']"))
                optionen = tag_select.options # Liest alle verfügbaren Ziehungsdaten im aktuellen Jahr.

                for i in range(len(optionen)): #Iteriert durch jeden Ziehungstag im Jahr.
                    tag_select = Select(self.driver.find_element(By.CSS_SELECTOR, "select[id^='daySelect-select']"))
                    # Ermittelt den internen Wert für die Dropdown-Auswahl (value) und das sichtbare Datum (z. B. „21.06. (Mittwoch)”).
                    option = tag_select.options[i]
                    tag_value = option.get_attribute("value")
                    datum = option.text.strip()

                    try:
                        # Wählt das Datum und ruft die Lottozahlen ab.
                        self.lade_jahr_und_tag(jahr, tag_value)
                        eintrag = self.extrahiere_daten(jahr, datum)

                        # Wenn mindestens 3 Zahlen vorhanden, wird die Ziehung als gültig gespeichert.
                        if all([eintrag["zahl_1"], eintrag["zahl_2"], eintrag["zahl_3"]]):
                            daten.append(eintrag)
                        else:
                            raise ValueError("Unvollständige Zahlen")

                    except Exception as e1:
                        print(f"⚠️ Fehler bei Ziehung {i} in Jahr {jahr}, erster Versuch: {e1}")
                        time.sleep(2)
                        # Zweiter Versuch, dann wird der Fehler samt Jahr und Datum dokumentiert.
                        try:
                            self.lade_jahr_und_tag(jahr, tag_value)
                            eintrag = self.extrahiere_daten(jahr, datum)
                            if all([eintrag["zahl_1"], eintrag["zahl_2"], eintrag["zahl_3"]]):
                                daten.append(eintrag)
                            else:
                                raise ValueError("Unvollständige Zahlen beim zweiten Versuch")
                        except Exception as e2:
                            print(f"❌ Fehler bei Ziehung {i} in Jahr {jahr} auch im zweiten Versuch: {e2}")
                            self.fehlerhafte_ziehungen.append({
                                "jahr": jahr,
                                "datum": datum,
                                "grund": str(e2)
                            })

            except Exception as e:
                print(f"❌ Fehler beim Laden der Tage in Jahr {jahr}: {e}")

        return daten

    # Exportiert alle extrahierten Daten sortiert nach Datum als Excel-Datei & speichert Fehler als JSON.
    def exportiere_excel(self, daten):
        df = pd.DataFrame(daten)
        df["sort_datum"] = df["datum"].str.extract(r"(\d{2}\.\d{2})").iloc[:, 0] + "." + df["jahr"].astype(str)
        df["sort_datum"] = pd.to_datetime(df["sort_datum"], format="%d.%m.%Y", errors="coerce")
        df.sort_values(by=["jahr", "sort_datum"], inplace=True)
        df.drop(columns=["sort_datum"], inplace=True)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        path = os.path.join(DATA_PATH, f"alle_lottoziehungen_{timestamp}.xlsx")
        df.to_excel(path, index=False)
        print(f"✅ Excel-Datei gespeichert: {path}")

        if self.fehlerhafte_ziehungen:
            fehler_path = os.path.join(DATA_PATH, f"fehlerhafte_ziehungen_{timestamp}.json")
            pd.DataFrame(self.fehlerhafte_ziehungen).to_json(fehler_path, orient="records", indent=2)
            print(f"⚠️ Fehlerhafte Ziehungen gespeichert unter: {fehler_path}")

    # Beendet die Selenium WebDriver-Sitzung.
    def beenden(self):
        self.driver.quit()

# === Hauptausführung ===
if __name__ == "__main__":
    scraper = LottoScraper()
    daten = scraper.extrahiere_alle_daten(start=1955, ende=1956)  # Beispiel-Range
    scraper.exportiere_excel(daten)
    scraper.beenden()
