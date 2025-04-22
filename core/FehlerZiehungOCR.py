import os
import re
import json
from datetime import datetime

# (venv) E:\Extracta>E:\Extracta\venv\Scripts\python.exe core/FehlerZiehungOCR.py
class FehlerZiehungOCR:
    def __init__(self, verzeichnis="data"):
        self.verzeichnis = verzeichnis
        self.fehlerdatei_path = self.finde_neueste_fehlerdatei()
        self.ziehungen = []

    def finde_neueste_fehlerdatei(self):
        """Sucht die neueste 'fehlerhafte_ziehungen_*.json'-Datei im data/-Verzeichnis."""
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
