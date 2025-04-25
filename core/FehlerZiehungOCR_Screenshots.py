"""
Modulname: FehlerZiehungOCR_Screenshots.py
Pfad:     core/FehlerZiehungOCR_Screenshots.py
Zweck:    Erneuter Screenshot-Versuch fehlgeschlagener Lottoziehungen (aus .json-Datei)
Website:  https://www.lotto.de/lotto-6aus49/lottozahlen

Beschreibung:
Dieses Skript lädt die zuletzt gespeicherte Datei mit fehlerhaften Ziehungen und
führt eine erneute Navigation zur Lotto-Website durch, um Screenshots der entsprechenden Ziehungen zu speichern.
Dies ist nützlich für die spätere manuelle Kontrolle oder Texterkennung (OCR).

Funktionen:
- Sucht nach der neuesten JSON-Datei mit fehlerhaften Ziehungen
- Initialisiert einen sichtbaren Chrome-Browser für Debugging-Zwecke
- Navigiert zur richtigen Ziehung über Jahr und Datumsauswahl
- Erstellt Screenshots der Ziehungsseite
- Speichert Metadaten zu den erstellten Screenshots als JSON

Abhängigkeiten:
- Selenium
- JSON
- datetime
- OS

Verwendung:
>>> (venv) PS C:\Extracta> python core/FehlerZiehungOCR_Screenshots.py
"""


import os
import json
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = "https://www.lotto.de/lotto-6aus49/lottozahlen"
DATA_PATH = "data"
SCREENSHOT_PATH = os.path.join(DATA_PATH, "screenshots")
os.makedirs(SCREENSHOT_PATH, exist_ok=True)

def finde_neueste_fehlerdatei():
    fehler_files = [f for f in os.listdir(DATA_PATH) if f.startswith("fehlerhafte_ziehungen_") and f.endswith(".json")]
    if not fehler_files:
        return None
    fehler_files.sort(reverse=True)
    return os.path.join(DATA_PATH, fehler_files[0])

def lade_fehlerhafte_ziehungen(pfad):
    with open(pfad, encoding="utf-8") as f:
        return json.load(f)

def initialisiere_browser():
    chrome_options = Options()
    # chrome_options.add_argument("--headless=new")  # für Debug ausgeschaltet
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(service=Service("tools/chromedriver.exe"), options=chrome_options)

def finde_tag_value(driver, ziel_datum):
    try:
        tag_select = Select(driver.find_element(By.CSS_SELECTOR, "select[id^='daySelect-select']"))
        for option in tag_select.options:
            if ziel_datum.strip() in option.text.strip():
                return option.get_attribute("value")
    except Exception as e:
        print(f"❌ Fehler beim Ermitteln von tag_value für {ziel_datum}: {e}")
    return None

def lade_ziehung(driver, jahr, tag_value):
    driver.get(BASE_URL)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "select[id^='selectedYear-select']")))
    Select(driver.find_element(By.CSS_SELECTOR, "select[id^='selectedYear-select']")).select_by_value(str(jahr))
    time.sleep(1)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "select[id^='daySelect-select']")))
    Select(driver.find_element(By.CSS_SELECTOR, "select[id^='daySelect-select']")).select_by_value(tag_value)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".DrawNumbersCollection__container .LottoBall")))
    time.sleep(0.5)

def erstelle_screenshot(driver, jahr, datum, tag_value):
    try:
        lade_ziehung(driver, jahr, tag_value)
        screenshot_name = f"screenshot_{jahr}_{datum.replace('.', '').replace(' ', '').replace('(', '').replace(')', '')}.png"
        screenshot_path = os.path.join(SCREENSHOT_PATH, screenshot_name)
        driver.save_screenshot(screenshot_path)
        print(f"✅ Screenshot gespeichert: {screenshot_path}")
        return screenshot_path
    except Exception as e:
        print(f"❌ Fehler bei Screenshot {jahr} {datum}: {e}")
        return None

def hauptprozess():
    pfad = finde_neueste_fehlerdatei()
    if not pfad:
        print("❌ Keine fehlerhafte_ziehungen_*.json gefunden!")
        return

    print(f"✅ Fehlerhafte Ziehungen geladen aus: {pfad}")
    ziehungen = lade_fehlerhafte_ziehungen(pfad)
    driver = initialisiere_browser()

    screenshots = []
    for eintrag in ziehungen:
        jahr = eintrag.get("jahr")
        datum = eintrag.get("datum")
        tag_value = eintrag.get("tag_value")

        if not tag_value:
            try:
                driver.get(BASE_URL)
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "select[id^='selectedYear-select']")))
                Select(driver.find_element(By.CSS_SELECTOR, "select[id^='selectedYear-select']")).select_by_value(str(jahr))
                time.sleep(1)
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "select[id^='daySelect-select']")))
                tag_value = finde_tag_value(driver, datum)
                if not tag_value:
                    print(f"❌ Kein passendes tag_value für {datum} ({jahr})")
                    continue
            except Exception as e:
                print(f"❌ Fehler beim Auffinden von tag_value für {datum} ({jahr}): {e}")
                continue

        pfad = erstelle_screenshot(driver, jahr, datum, tag_value)
        if pfad:
            screenshots.append({"jahr": jahr, "datum": datum, "tag_value": tag_value, "screenshot": pfad})

    driver.quit()
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    outpath = os.path.join(DATA_PATH, f"screenshots_mit_daten_{timestamp}.json")
    with open(outpath, "w", encoding="utf-8") as f:
        json.dump(screenshots, f, ensure_ascii=False, indent=2)
    print(f"✅ Alle Screenshots abgeschlossen. {len(screenshots)} gespeichert → {outpath}")

if __name__ == "__main__":
    hauptprozess()
    """                                                                                                                                  
    Achtung, die Klasse funktioniert sehr gut, aber einige Bilder werden zu schnell
    gemacht, so dass die richtigen Zahlen nicht geladen werden und die Bilder mit den alten Zahlen gemacht werden.
    
    """
     
