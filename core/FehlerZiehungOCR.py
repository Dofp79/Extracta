'''
Modulname: FehlerZiehungOCR.py
Pfad:     core/FehlerZiehungOCR.py
Zweck:    Lädt die zuletzt generierte JSON-Datei mit fehlerhaften Ziehungen für spätere OCR-Verarbeitung.

Beschreibung:
Dieses Skript dient zur Analyse und Vorbereitung fehlerhafter Ziehungsdaten. Es durchsucht das `data`-Verzeichnis
nach der neuesten Datei im Format `fehlerhafte_ziehungen_*.json` und lädt deren Inhalt. Diese Daten können
später für Screenshot-Erstellung oder OCR-Extraktion weiterverwendet werden.

Funktionen:
- Sucht automatisch die neueste Datei mit fehlerhaften Ziehungen
- Lädt den Inhalt als Liste von Dictionaries
- Bietet Vorschau der Datenstruktur für spätere Weiterverarbeitung

Abhängigkeiten:
- re
- os
- json
- datetime

Verwendung:
>>> (venv) C:\Extracta> C:\Extracta\venv\Scripts\python.exe core/FehlerZiehungOCR.py
'''

import os
import re
import json
from datetime import datetime

class FehlerZiehungOCR:
    def __init__(self, verzeichnis="data"):
         # Initialisiert mit Zielverzeichnis und sucht die neueste Fehlerdatei
        self.verzeichnis = verzeichnis
        self.fehlerdatei_path = self.finde_neueste_fehlerdatei()
        self.ziehungen = []

    def finde_neueste_fehlerdatei(self):
        # Sucht die neueste 'fehlerhafte_ziehungen_*.json'-Datei im data/-Verzeichnis.
        pattern = re.compile(r"fehlerhafte_ziehungen_\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}\.json")
        try:
            fehlerdateien = [
                f for f in os.listdir(self.verzeichnis)
                if pattern.match(f)
            ]
        except FileNotFoundError:
            print(f"Verzeichnis '{self.verzeichnis}' wurde nicht gefunden.")
            return None

        if not fehlerdateien:
            print("⚠️ Keine Datei vom Typ 'fehlerhafte_ziehungen_*.json' gefunden.")
            return None

        fehlerdateien.sort(reverse=True)
        return os.path.join(self.verzeichnis, fehlerdateien[0])

    def lade_fehlerhafte_ziehungen(self):
        """Lädt die Daten aus der JSON-Datei."""
        if not self.fehlerdatei_path:
            print("❌ Kein Fehlerdateipfad definiert.")
            return []

        with open(self.fehlerdatei_path, "r", encoding="utf-8") as f:
            self.ziehungen = json.load(f)
        print(f"✅ {len(self.ziehungen)} fehlerhafte Ziehungen geladen aus:\n→ {self.fehlerdatei_path}")
        return self.ziehungen

# Instanziieren und laden
ocr_loader = FehlerZiehungOCR()
fehlerhafte = ocr_loader.lade_fehlerhafte_ziehungen()
fehlerhafte[:2]  # Vorschau auf die ersten zwei Elemente
