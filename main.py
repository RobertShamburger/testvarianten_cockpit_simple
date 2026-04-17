import os
import csv
from anthropic import Anthropic
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


def send_to_claude(csv_content, prompt, api_key=None, model=None, max_tokens=None):
    """Sendet CSV-Inhalt und Prompt an Claude API."""
    if api_key is None:
        api_key = os.getenv('ANTHROPIC_API_KEY')
    if model is None:
        model = os.getenv('MODEL', 'claude-3-5-sonnet-20241022')
    if max_tokens is None:
        try:
            max_tokens = int(os.getenv('MAX_TOKENS', '1024'))
        except ValueError:
            max_tokens = 1024

    if not api_key:
        print("Fehler: ANTHROPIC_API_KEY nicht gesetzt.")
        return None

    try:
        # Zeige nur die ersten 4 Zeichen des API-Keys
        print(f"Verwende API-Key: {api_key[:4]}...")
        client = Anthropic(
            api_key=api_key,  # or os.getenv("POE_API_KEY")
            base_url="https://api.poe.com",
        )

        # Kombiniere Prompt mit CSV-Inhalt
        full_message = f"{prompt}\n\n--- Prozessdaten ---\n{csv_content}"

        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            messages=[
                {"role": "user", "content": full_message}
            ]
        )

        return response.content[0].text
    except Exception as e:
        print(f"Fehler bei der Claude API-Anfrage: {e}")
        return None


def main():
    load_env_file(ENV_FILE)

    csv_file = os.getenv('CSV_FILE', 'process.csv')
    prompt_file = os.getenv('PROMPT_FILE', 'prompt.txt')
    output_file = os.getenv('OUTPUT_FILE', 'claudeAnalysis.csv')
    model = os.getenv('MODEL', 'claude-sonnet-4-6')

    print(f"Lese CSV-Datei: {csv_file}")
    csv_content = read_csv_file(csv_file)
    if csv_content is None:
        return

    print(f"Lese Prompt-Datei: {prompt_file}")
    prompt = read_prompt_file(prompt_file)
    if prompt is None:
        return

    print("Sende Daten an Claude...")
    print(f"Verwendetes Modell: {model}")
    claudeAnalysis = send_to_claude(csv_content, prompt, model=model)

    if claudeAnalysis:
        print("\n--- Antwort von Claude ---")
        print(claudeAnalysis)
        
        # Überprüfe, ob die Ausgabedatei beschreibbar ist
        if not check_file_writable(output_file):
            print("Verarbeitung wird beendet.")
            return
        
        write_analysis_to_file(output_file, claudeAnalysis)
        print(f"Antwort wurde in '{output_file}' geschrieben.")
    else:
        print("Keine Antwort erhalten.")


def write_analysis_to_file(file_path, claudeAnalysis):
    """Schreibt die Claude-Antwort in eine CSV-Datei."""
    try:
        with open(file_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Analysis'])
            writer.writerow([claudeAnalysis])
    except Exception as e:
        print(f"Fehler beim Schreiben der Datei '{file_path}': {e}")


if __name__ == "__main__":
    main()
