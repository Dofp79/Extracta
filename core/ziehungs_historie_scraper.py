"""
Modul: core/ziehungs_historie_scraper.py
Ziel:
- Vollständiger Abruf aller Lottoziehungen von 1955-2025
- Interagiert mit dem Jahr-Dropdown auf lotto.de
- Extrahiert Datum, Zahlen, Superzahl je Ziehung
- Speichert jedes Jahr als JSON-Datei
"""

import os
import time
import json
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from model.lotto_model import LottoZiehung

# Globale URL der LOTTO-Archivseite
BASE_URL = "https://www.lotto.de/lotto-6aus49/lottozahlen"

# Browser-Driver Konfiguration
DRIVER_PATHS = {
    "chrome": os.path.join("tools", "chromedriver.exe"),
    "firefox": os.path.join("tools", "geckodriver.exe"),
    "edge": os.path.join("tools", "msedgedriver.exe"),
}

class LottoHistorieScraper:
    def __init__(self, browser="chrome"):
        self.browser = browser.lower()
        self.driver = self._starte_browser()
        self.wait = WebDriverWait(self.driver, 15)
        self.speicherpfad = os.path.join("data", "ziehungen_historie")
        os.makedirs(self.speicherpfad, exist_ok=True)

    def _starte_browser(self):
        if self.browser == "chrome":
            service = ChromeService(executable_path=DRIVER_PATHS["chrome"])
            options = webdriver.ChromeOptions()
            options.add_argument("--headless")
            return webdriver.Chrome(service=service, options=options)
        elif self.browser == "firefox":
            service = FirefoxService(executable_path=DRIVER_PATHS["firefox"])
            options = webdriver.FirefoxOptions()
            options.add_argument("--headless")
            return webdriver.Firefox(service=service, options=options)
        elif self.browser == "edge":
            service = EdgeService(executable_path=DRIVER_PATHS["edge"])
            options = webdriver.EdgeOptions()
            options.add_argument("--headless")
            return webdriver.Edge(service=service, options=options)
        else:
            raise ValueError("Unterstützter Browser: chrome, firefox, edge")

    def lade_jahr(self, jahr: int):
        self.driver.get(BASE_URL)
        time.sleep(3)
        self.driver.save_screenshot(f"screenshot_{jahr}.png")

        try:
            jahr_selector = "div.Select--year select"
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, jahr_selector)))
            jahr_dropdown = self.driver.find_element(By.CSS_SELECTOR, jahr_selector)

            for option in jahr_dropdown.find_elements(By.TAG_NAME, "option"):
                if option.text.strip() == str(jahr):
                    option.click()
                    break
            else:
                raise ValueError(f"\u26a0\ufe0f Jahr {jahr} nicht im Dropdown gefunden.")

            time.sleep(3)

        except Exception as e:
            print(f"❌ Fehler beim Laden des Jahres {jahr}: {e}")
            self.driver.save_screenshot(f"screenshot_error_{jahr}.png")
            raise

    def extrahiere_ziehungen(self):
        ziehungen = []
        eintraege = self.driver.find_elements(By.CSS_SELECTOR, ".WinningNumbers")
        for eintrag in eintraege:
            try:
                datum = eintrag.find_element(By.TAG_NAME, "h4").text.strip()
                zahlen = [int(el.text.strip()) for el in eintrag.find_elements(By.CSS_SELECTOR, ".lotto-ball")[:6]]
                superzahl = int(eintrag.find_element(By.CSS_SELECTOR, ".superzahl").text.strip())
                ziehungen.append(LottoZiehung(datum=datum, zahlen=zahlen, superzahl=superzahl).to_dict())
            except Exception as e:
                print("\u26a0\ufe0f Fehler beim Eintrag:", e)
        return ziehungen

    def speichere_jahr(self, jahr: int, ziehungen: list):
        pfad = os.path.join(self.speicherpfad, f"ziehungen_{jahr}.json")
        with open(pfad, "w", encoding="utf-8") as f:
            json.dump(ziehungen, f, indent=2, ensure_ascii=False)
        print(f"[\u2713] Gespeichert: {pfad}")

    def scrape_alle_jahre(self, start=1955, ende=2025):
        for jahr in range(start, ende + 1):
            print(f" Bearbeite Jahr {jahr} …")
            self.lade_jahr(jahr)
            ziehungen = self.extrahiere_ziehungen()
            self.speichere_jahr(jahr, ziehungen)

    def beenden(self):
        self.driver.quit()


# Testlauf
if __name__ == "__main__":
    scraper = LottoHistorieScraper("chrome")
    scraper.scrape_alle_jahre(2024, 2025)
    scraper.beenden()


def lade_jahr(self, jahr: int):
    self.driver.get(BASE_URL)
    time.sleep(3)
    self.driver.save_screenshot(f"screenshot_{jahr}.png")

    try:
        # Finde alle <select>-Felder und suche das mit Jahresoptionen
        dropdowns = self.driver.find_elements(By.TAG_NAME, "select")
        jahr_dropdown = None

        for select in dropdowns:
            options = select.find_elements(By.TAG_NAME, "option")
            for option in options:
                if option.text.strip() == str(jahr):
                    jahr_dropdown = select
                    option.click()
                    break
            if jahr_dropdown:
                break

        if not jahr_dropdown:
            raise ValueError(f"⚠️ Jahr {jahr} nicht im Dropdown gefunden.")

        time.sleep(3)

    except Exception as e:
        print(f"❌ Fehler beim Laden des Jahres {jahr}: {e}")
        self.driver.save_screenshot(f"screenshot_error_{jahr}.png")
        raise
