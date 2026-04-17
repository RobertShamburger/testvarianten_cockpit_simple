"""
Utility functions for the testvarianten_cockpit_simple project.
"""

def check_file_writable(file_path):
    """
    Überprüft, ob eine Datei beschreibbar ist.
    Gibt True zurück, wenn die Datei beschreibbar ist, sonst False.
    """
    try:
        # Versuche, die Datei im Schreibmodus zu öffnen
        with open(file_path, 'a', encoding='utf-8'):
            pass
        return True
    except (PermissionError, OSError) as e:
        print(f"Fehler: Datei '{file_path}' kann nicht beschrieben werden: {e}")
        print("Möglicherweise wird die Datei von einer anderen Anwendung verwendet.")
        return False