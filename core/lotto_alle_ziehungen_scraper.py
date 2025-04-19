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
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(service=Service("tools/chromedriver.exe"), options=chrome_options)

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

        def neue_zahl_geladen(driver):
            try:
                neue_zahl = driver.find_elements(By.CSS_SELECTOR, ".DrawNumbersCollection__container")[0]\
                              .find_elements(By.CLASS_NAME, "LottoBall")[0].text.strip()
                return neue_zahl != "" and neue_zahl != alte_zahl
            except:
                return False

        WebDriverWait(self.driver, 10).until(neue_zahl_geladen)
        time.sleep(0.5)

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

    def extrahiere_alle_daten(self, start=1955, ende=2025):
        daten = []
        for jahr in range(start, ende + 1):
            print(f" Verarbeite Jahr {jahr} …")
            self.driver.get(BASE_URL)
            time.sleep(2)

            jahr_select = Select(self.driver.find_element(By.CSS_SELECTOR, "select[id^='selectedYear-select']"))
            jahr_select.select_by_value(str(jahr))
            time.sleep(2)

            try:
                tag_select = Select(self.driver.find_element(By.CSS_SELECTOR, "select[id^='daySelect-select']"))
                optionen = tag_select.options

                for i in range(len(optionen)):
                    try:
                        tag_select = Select(self.driver.find_element(By.CSS_SELECTOR, "select[id^='daySelect-select']"))
                        option = tag_select.options[i]
                        tag_value = option.get_attribute("value")
                        datum = option.text.strip()

                        self.lade_jahr_und_tag(jahr, tag_value)
                        eintrag = self.extrahiere_daten(jahr, datum)
                        daten.append(eintrag)

                    except Exception as e:
                        print(f" Fehler bei Ziehung {i} in Jahr {jahr}: {e}")

            except Exception as e:
                print(f" Fehler beim Laden der Tage in Jahr {jahr}: {e}")

        return daten

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

    def beenden(self):
        self.driver.quit()

# === Hauptausführung ===
if __name__ == "__main__":
    scraper = LottoScraper()
    daten = scraper.extrahiere_alle_daten(start=1955, ende=1956)  # Testlauf für 2 Jahre
    scraper.exportiere_excel(daten)
    scraper.beenden()
