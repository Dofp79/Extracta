"""
Multibrowser-Scraper für Lottozahlen von lotto.de

Ziel:
- Öffnet die Website mit Selenium
- Wartet auf die geladenen Zahlen
- Extrahiert Lottozahlen, Superzahl & Quoten
- Unterstützt Chrome, Firefox & Edge
- Gibt ein LottoZiehung-Objekt zurück
"""

import os
import sys
import time
import datetime

# Selenium: Steuerung echter Browser
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Projektverzeichnis zur sys.path hinzufügen, um Model-Import zu ermöglichen
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from model.lotto_model import LottoZiehung

# Pfade zu den verschiedenen Browser-Treibern
DRIVER_PATHS = {
    "chrome": os.path.join("tools", "chromedriver.exe"),
    "firefox": os.path.join("tools", "geckodriver.exe"),
    "edge": os.path.join("tools", "msedgedriver.exe"),
}

# Zielseite mit den aktuellen Lottozahlen
LOTTO_URL = "https://www.lotto.de/lotto-6aus49/lottozahlen"


def create_driver(browser: str = "chrome"):
    """
    Erstellt und gibt den passenden WebDriver zurück.
    Unterstützt: chrome, firefox, edge
    """
    browser = browser.lower()  # robust gegen Groß-/Kleinschreibung
    driver = None

    # Chrome-Driver konfigurieren
    if browser == "chrome":
        service = ChromeService(executable_path=DRIVER_PATHS["chrome"])
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")  # Headless = kein sichtbares Fenster
        driver = webdriver.Chrome(service=service, options=options)

    # Firefox-Driver konfigurieren
    elif browser == "firefox":
        service = FirefoxService(executable_path=DRIVER_PATHS["firefox"])
        options = webdriver.FirefoxOptions()
        options.add_argument("--headless")
        driver = webdriver.Firefox(service=service, options=options)

    # Edge-Driver konfigurieren
    elif browser == "edge":
        service = EdgeService(executable_path=DRIVER_PATHS["edge"])
        options = webdriver.EdgeOptions()
        options.add_argument("--headless")
        driver = webdriver.Edge(service=service, options=options)

    else:
        raise ValueError(" Ungültiger Browser. Unterstützt: chrome, firefox, edge")

    return driver


def hole_aktuelle_ziehung(browser: str = "chrome") -> LottoZiehung:
    """
    Öffnet die Seite mit dem gewählten Browser, extrahiert Ziehungsdaten.
    Gibt ein LottoZiehung-Objekt zurück.
    """
    print(f" Starte Browser: {browser}")
    driver = create_driver(browser)
    driver.get(LOTTO_URL)

    try:
        wait = WebDriverWait(driver, 20)  # längere Wartezeit für dynamisches Laden

        # Warten, bis das Hauptlayout geladen ist (zeigt an, dass React fertig ist)
        print(" Warte auf <main.page--lotto6aus49> ...")
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "main.page--lotto6aus49")))

        # Sicherheitswartezeit: Gibt JS Zeit, alles zu bauen
        print(" Kurze Pause für finale DOM-Erzeugung (JS)...")
        time.sleep(2)

        #  Ziehungsdatum holen
        datum_element = driver.find_element(By.TAG_NAME, "time")
        datum = datum_element.get_attribute("datetime")

        #  Lottozahlen (6 aus 49)
        zahlen_elements = driver.find_elements(By.CSS_SELECTOR, ".lotto-zahlen .zahl")
        zahlen = [int(elem.text.strip()) for elem in zahlen_elements[:6]]

        #  Superzahl
        superzahl_elem = driver.find_element(By.CSS_SELECTOR, ".lotto-superzahl .zahl")
        superzahl = int(superzahl_elem.text.strip())

        #  Gewinnquoten
        quoten = {}
        quotenzeilen = driver.find_elements(By.CSS_SELECTOR, ".gewinnquoten .gewinnreihe")
        for zeile in quotenzeilen:
            try:
                klasse = zeile.find_element(By.CSS_SELECTOR, ".klasse").text.strip()
                betrag = zeile.find_element(By.CSS_SELECTOR, ".gewinnbetrag").text.strip()
                quoten[klasse] = betrag
            except Exception:
                continue  # Unvollständige Zeile ignorieren

        return LottoZiehung(datum=datum, zahlen=zahlen, superzahl=superzahl, quoten=quoten)

    except Exception as e:
        # HTML-Dump bei Fehler zur Analyse
        with open("debug_output.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print(" HTML-Dump gespeichert als debug_output.html")
        raise e

    finally:
        driver.quit()
        print(f" {browser} wurde sauber geschlossen.")


# Hauptblock: Wird nur ausgeführt, wenn Datei direkt gestartet wird
if __name__ == "__main__":
    try:
        # Versuche die Ziehung mit dem Chrome-Browser zu holen
        ziehung = hole_aktuelle_ziehung("chrome")
        print(ziehung.to_dict())

    except Exception as e:
        print(" FEHLER beim Ausführen des Scrapers:")
        print(e)
