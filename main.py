import os
import csv
from anthropic import Anthropic

def read_csv_file(file_path):
    """Liest eine CSV-Datei und gibt den Inhalt als formatierten String zurück."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            rows = list(reader)
            
            if not rows:
                print(f"Warnung: CSV-Datei '{file_path}' ist leer.")
                return None
            
            # Formatiere CSV-Inhalt als lesbaren String
            csv_content = "Prozessschritte:\n"
            for i, row in enumerate(rows, 1):
                csv_content += f"\nSchritt {i}:\n"
                for key, value in row.items():
                    csv_content += f"  {key}: {value}\n"
            
            return csv_content
    except FileNotFoundError:
        print(f"Fehler: CSV-Datei '{file_path}' nicht gefunden.")
        return None
    except Exception as e:
        print(f"Fehler beim Lesen der CSV-Datei: {e}")
        return None

def read_prompt_file(file_path):
    """Liest eine Prompt-Datei aus."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Fehler: Prompt-Datei '{file_path}' nicht gefunden.")
        return None
    except Exception as e:
        print(f"Fehler beim Lesen der Prompt-Datei: {e}")
        return None

def send_to_claude(csv_content, prompt, api_key=None):
    """Sendet CSV-Inhalt und Prompt an Claude API."""
    if api_key is None:
        api_key = os.getenv('ANTHROPIC_API_KEY')
    
    if not api_key:
        print("Fehler: ANTHROPIC_API_KEY nicht gesetzt.")
        return None
    
    try:
        client = Anthropic(api_key=api_key)
        
        # Kombiniere Prompt mit CSV-Inhalt
        full_message = f"{prompt}\n\n--- Prozessdaten ---\n{csv_content}"
        
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",  # Oder: claude-3-opus-20240229, claude-3-haiku-20240307
            max_tokens=1024,
            messages=[
                {"role": "user", "content": full_message}
            ]
        )
        
        return response.content[0].text
    except Exception as e:
        print(f"Fehler bei der Claude API-Anfrage: {e}")
        return None

def main():
    # Hart kodierte Dateinamen
    csv_file = 'prozess.csv'
    prompt_file = 'prompt.txt'
    
    print(f"Lese CSV-Datei: {csv_file}")
    csv_content = read_csv_file(csv_file)
    if csv_content is None:
        return
    
    print(f"Lese Prompt-Datei: {prompt_file}")
    prompt = read_prompt_file(prompt_file)
    if prompt is None:
        return
    
    print("Sende Daten an Claude...")
    result = send_to_claude(csv_content, prompt)
    
    if result:
        print("\n--- Antwort von Claude ---")
        print(result)
    else:
        print("Keine Antwort erhalten.")

if __name__ == "__main__":
    main()