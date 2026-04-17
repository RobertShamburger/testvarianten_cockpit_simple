import os
import csv
import ast
from pathlib import Path

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
    replacements_str = os.getenv('REPLACEMENTS', '')
    output_file = 'new-process.csv'
    
    if not os.path.exists(input_file):
        print(f"Fehler: Eingabedatei '{input_file}' nicht gefunden.")
        return
    
    if not replacements_str:
        print("Fehler: REPLACEMENTS nicht in .env-Datei definiert.")
        return
    
    print(f"Lese CSV-Datei: {input_file}")
    print(f"REPLACEMENTS: {replacements_str}")
    
    # Parse Replacements
    replacements = parse_replacements(replacements_str)
    
    if not replacements:
        print("Fehler: Keine gültigen Replacements definiert.")
        return
    
    print(f"\nVerarbeitete Replacements:")
    for zeile, alt_wert, neu_wert in replacements:
        print(f"  Zeile {zeile}: '{alt_wert}' -> '{neu_wert}'")
    
    # Verarbeite CSV
    print(f"\nVerarbeite CSV...")
    process_csv(input_file, output_file, replacements)


if __name__ == "__main__":
    main()
