import os
import csv
import ast
from pathlib import Path
from utils import check_file_writable

ENV_FILE = '.env'


def load_env_file(path):
    """Lädt Umgebungsvariablen aus einer .env-Datei."""
    if not os.path.exists(path):
        return
    try:
        with open(path, 'r', encoding='utf-8') as file:
            for raw_line in file:
                line = raw_line.strip()
                if not line or line.startswith('#') or '=' not in line:
                    continue
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key and value:
                    os.environ[key] = value
    except Exception as e:
        print(f"Fehler beim Laden der .env-Datei '{path}': {e}")


def generate_mock_value(value):
    """
    Generiert einen Mock-Wert basierend auf dem Typ des Eingabewerts.
    """
    value_str = str(value).strip()
    
    # Versuche, den Wert als Zahl zu interpretieren
    try:
        # Überprüfe auf Integer
        if '.' not in value_str:
            num = int(value_str)
            return str(num + 1)
        else:
            # Überprüfe auf Float
            num = float(value_str)
            return str(num + 0.1)
    except ValueError:
        pass
    
    # Für Strings: Anhängen von "_modified"
    return f"{value_str}_modified"


def extract_replacements_from_claude_analysis(file_path):
    """
    Extrahiert die REPLACEMENTS-Struktur aus claudeAnalysis.csv.
    Filtert Zeilen mit "x" in der "Variieren"-Spalte.
    Generiert Mock-Werte für Neuer-Wert.
    Rückgabe: Liste von Tupeln (Zeile, Alt-Wert, Neu-Wert)
    """
    replacements = []
    
    if not os.path.exists(file_path):
        print(f"Info: {file_path} nicht gefunden, verwende Fallback aus .env")
        return replacements
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            all_content = file.read()
        
        # Extrahiere nur den CSV-Teil zwischen ```csv und ```
        start_marker = '```csv'
        end_marker = '```'
        
        start_idx = all_content.find(start_marker)
        if start_idx == -1:
            print(f"Info: Keine CSV-Daten in {file_path} gefunden")
            return replacements
        
        start_idx += len(start_marker)
        end_idx = all_content.find(end_marker, start_idx)
        if end_idx == -1:
            end_idx = len(all_content)
        
        csv_content = all_content[start_idx:end_idx].strip()
        csv_lines = [line.strip() for line in csv_content.split('\n') if line.strip()]
        
        if len(csv_lines) < 2:
            print(f"Info: Keine Datensätze in {file_path}")
            return replacements
        
        # Parse Header
        header_line = csv_lines[0]
        headers = [h.strip().strip('"').lower() for h in header_line.split(';')]
        
        # Finde Spalten-Indizes
        variieren_idx = None
        zeile_idx = None
        data_wert_idx = None
        
        for i, header in enumerate(headers):
            if 'variieren' in header:
                variieren_idx = i
            elif 'zeile' in header:
                zeile_idx = i
            elif 'data-wert' in header or 'data_wert' in header:
                data_wert_idx = i
        
        if variieren_idx is None or zeile_idx is None or data_wert_idx is None:
            print(f"Warnung: Erforderliche Spalten nicht gefunden")
            return replacements
        
        # Verarbeite Datensätze
        for line_num, line in enumerate(csv_lines[1:], start=2):
            parts = [p.strip().strip('"') for p in line.split(';')]
            
            if variieren_idx < len(parts):
                variieren_wert = parts[variieren_idx].lower().strip()
                if variieren_wert == 'x':
                    if zeile_idx < len(parts) and data_wert_idx < len(parts):
                        try:
                            zeile = int(parts[zeile_idx])
                            alt_wert = parts[data_wert_idx]
                            neu_wert = generate_mock_value(alt_wert)
                            
                            replacements.append((zeile, alt_wert, neu_wert))
                            print(f"Extrahiert: Zeile {zeile}: '{alt_wert}' -> '{neu_wert}'")
                        except (ValueError, IndexError) as e:
                            print(f"Warnung: Fehler bei Zeile {line_num}: {e}")
        
        if replacements:
            print(f"Info: {len(replacements)} Ersetzungen aus {file_path} extrahiert")
        else:
            print(f"Info: Keine Zeilen mit 'x' in Variieren-Spalte gefunden")
        
        return replacements
    
    except Exception as e:
        print(f"Fehler beim Lesen von {file_path}: {e}")
        import traceback
        traceback.print_exc()
        return replacements


def parse_replacements(replacements_str):
    """
    Parst die REPLACEMENTS-Variable aus der .env-Datei.
    Format: [(Zeile, Alt-Wert, Neu-Wert), (Zeile, Alt-Wert, Neu-Wert), ...]
    Rückgabe: Liste von Tupeln (Zeile, Alt-Wert, Neu-Wert)
    """
    replacements = []
    if not replacements_str:
        return replacements
    
    try:
        # Parse die String-Darstellung als Python-Literal
        data = ast.literal_eval(replacements_str.strip())
        
        # Überprüfe, ob es eine Liste ist
        if not isinstance(data, list):
            print(f"Fehler: REPLACEMENTS muss eine Liste sein, nicht {type(data).__name__}")
            return replacements
        
        # Verarbeite jedes Tupel
        for item in data:
            if isinstance(item, tuple) and len(item) == 3:
                zeile, alt_wert, neu_wert = item
                try:
                    zeile = int(zeile)
                    replacements.append((zeile, str(alt_wert), str(neu_wert)))
                except (ValueError, TypeError) as e:
                    print(f"Warnung: Konvertierungsfehler für Tupel {item}: {e}")
            else:
                print(f"Warnung: Ungültiges Tupel-Format: {item}")
    
    except (SyntaxError, ValueError) as e:
        print(f"Fehler beim Parsen der REPLACEMENTS: {e}")
    
    return replacements


def process_csv(input_file, output_file, replacements):
    """
    Liest CSV-Datei, ersetzt Datenwerte gemäß Replacements und speichert neue Datei.
    """
    try:
        # CSV-Datei einlesen
        with open(input_file, 'r', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter=';')
            rows = list(reader)
        
        if not rows:
            print(f"Fehler: CSV-Datei '{input_file}' ist leer.")
            return False
        
        # Header-Zeile (1-indexed)
        header = rows[0]
        data_index = None
        action_index = None
        
        # Finde die Indizes der 'Data'- und 'Action'-Spalten
        for i, col in enumerate(header):
            col_lower = col.strip().lower()
            if col_lower == 'data':
                data_index = i
            elif col_lower == 'action':
                action_index = i
        
        if data_index is None or action_index is None:
            print("Fehler: 'Data'- oder 'Action'-Spalte nicht gefunden.")
            return False
        
        # Erstelle eine Dictionary für schnelleren Zugriff auf Replacements
        # Key: (zeile_nummer, alt_wert) -> Wert: neu_wert
        replacement_dict = {}
        for zeile, alt_wert, neu_wert in replacements:
            replacement_dict[(zeile, alt_wert)] = neu_wert
        
        # Ersetze Datenwerte (Zeilen ab Zeile 2, da Zeile 1 ist der Header)
        changes_made = 0
        for zeile_nr in replacement_dict:
            row_index = zeile_nr[0]  # 1-indexed
            alt_wert = zeile_nr[1]
            neu_wert = replacement_dict[zeile_nr]
            
            # Konvertiere zu 0-indexed
            row_idx = row_index - 1
            
            if row_idx < 0 or row_idx >= len(rows):
                print(f"Warnung: Zeile {row_index} existiert nicht.")
                continue
            
            # Ersetze in Data-Spalte
            if data_index < len(rows[row_idx]):
                aktueller_wert = rows[row_idx][data_index].strip()
                if aktueller_wert == alt_wert or alt_wert == '':
                    rows[row_idx][data_index] = neu_wert
                    print(f"Zeile {row_index} [Data]: '{aktueller_wert}' -> '{neu_wert}'")
                    changes_made += 1
                else:
                    print(f"Warnung: Zeile {row_index} [Data] - erwarteter Wert '{alt_wert}' nicht gefunden (aktuell: '{aktueller_wert}')")
            
            # Ersetze in Action-Spalte
            if action_index < len(rows[row_idx]):
                action_wert = rows[row_idx][action_index]
                if alt_wert in action_wert:
                    neue_action = action_wert.replace(alt_wert, neu_wert)
                    rows[row_idx][action_index] = neue_action
                    print(f"Zeile {row_index} [Action]: '{alt_wert}' -> '{neu_wert}'")
                    changes_made += 1
                else:
                    print(f"Warnung: Zeile {row_index} [Action] - Wert '{alt_wert}' nicht gefunden")
        
        # Neue Datei speichern
        with open(output_file, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerows(rows)
        
        print(f"\n{changes_made} Ersetzungen durchgeführt.")
        print(f"Neue Datei erstellt: '{output_file}'")
        return True
    
    except Exception as e:
        print(f"Fehler bei der CSV-Verarbeitung: {e}")
        return False


def main():
    load_env_file(ENV_FILE)
    
    input_file = os.getenv('CSV_FILE', 'process.csv')
    claude_analysis_file = os.getenv('OUTPUT_FILE', 'claudeAnalysis.csv')
    output_file = 'new-process.csv'
    
    if not os.path.exists(input_file):
        print(f"Fehler: Eingabedatei '{input_file}' nicht gefunden.")
        return
    
    print(f"Lese CSV-Datei: {input_file}")
    
    # Versuche, REPLACEMENTS aus claudeAnalysis.csv zu extrahieren
    print(f"\nExtrahiere Replacements aus '{claude_analysis_file}'...")
    replacements = extract_replacements_from_claude_analysis(claude_analysis_file)
    
    # Falls keine Replacements extrahiert wurden, verwende Fallback aus .env
    if not replacements:
        print("\nVerwende Fallback-REPLACEMENTS aus .env")
        replacements_str = os.getenv('REPLACEMENTS', '')
        if replacements_str:
            replacements = parse_replacements(replacements_str)
            print(f"REPLACEMENTS aus .env: {replacements_str}")
        else:
            print("Fehler: Keine Replacements definiert und claudeAnalysis.csv nicht vorhanden/leer.")
            return
    
    if not replacements:
        print("Fehler: Keine gültigen Replacements definiert.")
        return
    
    print(f"\nVerarbeitete Replacements:")
    for zeile, alt_wert, neu_wert in replacements:
        print(f"  Zeile {zeile}: '{alt_wert}' -> '{neu_wert}'")
    
    # Verarbeite CSV
    print(f"\nVerarbeite CSV...")
    
    # Überprüfe, ob die Ausgabedatei beschreibbar ist
    if not check_file_writable(output_file):
        print("Verarbeitung wird beendet.")
        return
    
    process_csv(input_file, output_file, replacements)


if __name__ == "__main__":
    main()
