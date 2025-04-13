"""
Modul: core/haeufigkeit_speicher.py
Ziel:
- Speichert Häufigkeitsdaten der Lottozahlen
- Unterstützt drei Formate: JSON, CSV, Excel (.xlsx)
"""

import os
import json
import csv
import pandas as pd


class HaeufigkeitSpeicher:
    def __init__(self, speicherpfad="daten"):
        """
        Initialisiert den Speicherpfad.
        Falls das Verzeichnis nicht existiert, wird es erstellt.
        """
        self.speicherpfad = speicherpfad
        os.makedirs(speicherpfad, exist_ok=True)

    def speichere_json(self, daten: dict, dateiname: str = "haeufigkeit.json"):
        """
        Speichert die Häufigkeiten als JSON-Datei.
        """
        pfad = os.path.join(self.speicherpfad, dateiname)
        with open(pfad, "w", encoding="utf-8") as f:
            json.dump(daten, f, indent=2, ensure_ascii=False)
        print(f"[✓] JSON gespeichert: {pfad}")

    def speichere_csv(self, daten: dict, dateiname: str = "haeufigkeit.csv"):
        """
        Speichert die Häufigkeiten als CSV-Datei.
        """
        pfad = os.path.join(self.speicherpfad, dateiname)
        with open(pfad, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Zahl", "Häufigkeit"])
            for zahl, anzahl in daten.items():
                writer.writerow([zahl, anzahl])
        print(f"[✓] CSV gespeichert: {pfad}")

    def speichere_excel(self, daten: dict, dateiname: str = "haeufigkeit.xlsx"):
        """
        Speichert die Häufigkeiten als Excel-Datei.
        """
        pfad = os.path.join(self.speicherpfad, dateiname)
        df = pd.DataFrame(list(daten.items()), columns=["Zahl", "Häufigkeit"])
        df.to_excel(pfad, index=False)
        print(f"[✓] Excel gespeichert: {pfad}")

        

