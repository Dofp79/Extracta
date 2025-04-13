"""
13,04,2025 11:58
Scraper für Ziehungsstatistik von lotto.de mit Selenium
Ziel:
- Öffnet die Seite im Browser
- Wartet auf .StatisticsBar (JS-generiert)
- Extrahiert Lottozahl und deren Häufigkeit
- Gibt sortierte Liste aus
"""

import time
import os
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Stelle sicher, dass LottoZiehung importierbar wäre, falls gebraucht
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Lokaler Pfad zum ChromeDriver
CHROME_DRIVER_PATH = os.path.join("tools", "chromedriver.exe")

# Zielseite
STATISTIK_URL = "https://www.lotto.de/lotto-6aus49/statistik/ziehungshaeufigkeit"


def hole_statistik_mit_selenium() -> list[tuple[int, int]]:
    """
    Führt den Browser, wartet auf DOM, extrahiert Zahlen + Häufigkeit
    """
    # Chrome headless starten
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    service = ChromeService(executable_path=CHROME_DRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)

    try:
        print(" Öffne Seite …")
        driver.get(STATISTIK_URL)

        # Warte auf ein erstes Statistik-Element
        wait = WebDriverWait(driver, 15)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "StatisticsBar")))

        # Sicherheitshalber noch kurze Pause für Rendering
        time.sleep(1.5)

        # Alle Statistik-Balken holen
        statistik_elemente = driver.find_elements(By.CLASS_NAME, "StatisticsBar")

        daten = []
        for bar in statistik_elemente:
            try:
                zahl_elem = bar.find_element(By.CLASS_NAME, "LottoBall__circle")
                haeufigkeit_elem = bar.find_element(By.CLASS_NAME, "StatisticsBar__count")

                zahl = int(zahl_elem.get_attribute("aria-label").strip())
                haeufigkeit = int(haeufigkeit_elem.text.replace("×", "").strip())

                daten.append((zahl, haeufigkeit))
            except Exception as e:
                print(f" Fehler beim Extrahieren eines Balkens: {e}")
                continue

        return sorted(daten, key=lambda x: x[0])  # sortiere nach Lottozahl

    finally:
        driver.quit()
        print(" Browser beendet")


if __name__ == "__main__":
    daten = hole_statistik_mit_selenium()
    print(" Häufigkeiten:")
    for zahl, anz in daten:
        print(f"Zahl {zahl:2}: {anz}x")
