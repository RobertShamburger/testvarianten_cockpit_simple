# Testvarianten Cockpit Simple

Eine Python-Anwendung, die Prozessschritte aus einer CSV-Datei ausliest und mit einem benutzerdefinierten Prompt an die Claude AI-API (Anthropic) sendet.

## Funktionalität
- Liest Prozessschritte aus einer CSV-Datei (`prozess.csv`)
- Lädt einen Prompt aus einer Textdatei (`prompt.txt`)
- Sendet die Daten an Claude AI (Anthropic API)
- Gibt die KI-generierte Antwort aus

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
   oder in einer `.env`-Datei speichern

## Verwendung
1. Erstelle eine `prozess.csv` Datei im Projektverzeichnis mit deinen Prozessschritten (z. B. Spalten: `Schritt`, `Beschreibung`, `Dauer`, etc.)
2. Erstelle eine `prompt.txt` Datei mit deinem Prompt für Claude
3. Führe aus:
   ```bash
   python main.py
   ```
4. Die Anwendung liest beide Dateien, kombiniert sie und sendet sie an Claude

## Dateistruktur
```
.
├── main.py              # Hauptskript
├── prozess.csv          # Eingabe: Prozessschritte (CSV-Format)
├── prompt.txt           # Eingabe: Prompt für Claude
├── requirements.txt     # Python-Abhängigkeiten
└── README.md           # Diese Datei
```

## Abhängigkeiten
- `anthropic>=0.30.0` - Anthropic (Claude) API Client
- `requests>=2.25.0` - HTTP-Library

## Anpassungen
- Ändere die Dateinamen `prozess.csv` und `prompt.txt` in `main.py` für andere Dateien
- Passe das `model` in der `send_to_claude()`-Funktion an (z. B. `claude-3-opus-20240229` oder `claude-3-haiku-20240307`)
- Erhöhe `max_tokens` für längere Antworten