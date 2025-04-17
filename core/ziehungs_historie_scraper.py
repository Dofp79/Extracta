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
