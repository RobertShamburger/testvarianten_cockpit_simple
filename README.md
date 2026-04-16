# Testvarianten Cockpit Simple

Eine Python-Anwendung, die Prozessschritte aus einer CSV-Datei ausliest und mit einem benutzerdefinierten Prompt an die Claude AI-API (Anthropic) sendet.

## Funktionalität
- Liest Prozessschritte aus einer CSV-Datei (`process.csv`)
- Lädt einen Prompt aus einer Textdatei (`prompt.txt`)
- Sendet die Daten an Claude AI (Anthropic API)
- Gibt die KI-generierte Antwort aus und speichert sie in `claudeAnalysis.txt`

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
5. Die Antwort von Claude wird zusätzlich in `claudeAnalysis.txt` gespeichert

## Konfiguration
Die Datei `.env` kann folgende Werte enthalten:
- `ANTHROPIC_API_KEY`
- `CSV_FILE`
- `PROMPT_FILE`
- `OUTPUT_FILE`
- `MODEL`
- `MAX_TOKENS`

## Dateistruktur
```
.
├── main.py              # Hauptskript
├── process.csv          # Eingabe: Prozessschritte (CSV-Format)
├── prompt.txt           # Eingabe: Prompt für Claude
├── claudeAnalysis.txt   # Ausgabe: Claude-Antwort
├── requirements.txt     # Python-Abhängigkeiten
└── README.md           # Diese Datei
```

## Abhängigkeiten
- `anthropic>=0.30.0` - Anthropic (Claude) API Client
- `requests>=2.25.0` - HTTP-Library

## Anpassungen
- Ändere die Werte `CSV_FILE` und `PROMPT_FILE` in der `.env`-Datei, um andere Eingabedateien zu verwenden
- Passe das `MODEL` in der `.env` oder in `send_to_claude()` an (z. B. `claude-3-opus-20240229` oder `claude-3-haiku-20240307`)
- Erhöhe `MAX_TOKENS` für längere Antworten