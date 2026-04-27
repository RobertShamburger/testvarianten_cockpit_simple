# Testvarianten Cockpit Simple

Eine Python-Anwendung, die Prozessschritte aus einer CSV-Datei ausliest, mit einem benutzerdefinierten Prompt an die Claude AI-API (Anthropic) sendet und die Antwort in einer CSV-Datei speichert.

## Funktionalität
- Liest Prozessschritte aus einer CSV-Datei (`process.csv`)
- Lädt einen Prompt aus einer Textdatei (`prompt.txt`)
- Sendet die Daten an Claude AI (Anthropic API)
- Gibt die KI-generierte Antwort aus und speichert sie in `claudeAnalysis.csv`
- Optional: Verarbeitet `claudeAnalysis.csv` mit `process_replacements.py`, um `new-process.csv` zu erzeugen

## Installation
1. Python 3.8+ installieren
2. Abhängigkeiten installieren:
   ```bash
   pip install -r requirements.txt
   ```
3. API-Schlüssel setzen:
   ```bash
   export ANTHROPIC_API_KEY=dein-api-schluessel
   ```
   oder in einer `.env`-Datei speichern. Die Anwendung lädt beim Start automatisch Konfigurationen aus `.env`.

## Verwendung
1. Erstelle eine `process.csv` Datei im Projektverzeichnis mit deinen Prozessschritten (z. B. Spalten: `Schritt`, `Beschreibung`, `Dauer`, etc.)
2. Erstelle eine `prompt.txt` Datei mit deinem Prompt für Claude
3. Führe aus:
   ```bash
   python main.py
   ```
4. Die Anwendung liest beide Dateien, kombiniert sie und sendet sie an Claude
5. Die Antwort von Claude wird in `claudeAnalysis.csv` gespeichert

### Optional: Variationen verarbeiten
1. Führe `process_replacements.py` aus:
   ```bash
   python process_replacements.py
   ```
2. Das Skript versucht, `REPLACEMENTS` aus `claudeAnalysis.csv` zu extrahieren und schreibt die veränderte CSV in `new-process.csv`
3. Falls keine Werte aus `claudeAnalysis.csv` extrahiert werden können, kann `REPLACEMENTS` auch in `.env` definiert werden

## Konfiguration
Die Datei `.env` kann folgende Werte enthalten:
- `ANTHROPIC_API_KEY`
- `CSV_FILE`
- `PROMPT_FILE`
- `OUTPUT_FILE`
- `MODEL`
- `MAX_TOKENS`
- `REPLACEMENTS` (optional, für `process_replacements.py`)

## Dateistruktur
```
.
├── main.py              # Hauptskript
├── process_replacements.py # Skript zur Verarbeitung von Replacements
├── utils.py             # Hilfsfunktionen
├── process.csv          # Eingabe: Prozessschritte (CSV-Format)
├── prompt.txt           # Eingabe: Prompt für Claude
├── claudeAnalysis.csv   # Ausgabe: Claude-Antwort
├── requirements.txt     # Python-Abhängigkeiten
└── README.md            # Diese Datei
```

## Abhängigkeiten
- `anthropic>=0.30.0`
- `requests>=2.25.0`

## Anpassungen
- Ändere die Werte `CSV_FILE` und `PROMPT_FILE` in der `.env`-Datei, um andere Eingabedateien zu verwenden
- Passe das `MODEL` in der `.env` an, z. B. `claude-3-opus-20240229` oder `claude-3-haiku-20240307`
- Erhöhe `MAX_TOKENS` für längere Antworten
- Definiere optional `REPLACEMENTS` in `.env`, wenn `process_replacements.py` keine Werte aus `claudeAnalysis.csv` extrahieren kann