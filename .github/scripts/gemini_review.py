import os
import subprocess
from google import genai
from google.genai import types

# API Keys und Variablen laden
api_key = os.environ.get("GEMINI_API_KEY")
pr_number = os.environ.get("PR_NUMBER")

# Diff-Datei lesen
try:
    with open("pr_diff.txt", "r") as f:
        diff_content = f.read()
except FileNotFoundError:
    diff_content = "Kein Diff gefunden."

# Wenn der Diff leer ist, brechen wir ab
if not diff_content.strip():
    print("Keine Änderungen zum Reviewen.")
    exit(0)

# Meine Systemanweisung als kritischer Reviewer
system_instruction = """
Du bist der leitende kritische Code-Reviewer für eine botanische Computer-Vision-Pipeline.
Suche gezielt nach systematischen Fehlern, blinden Flecken und Architekturverletzungen:
1. Fehlen globale Exception-Catcher in der pipeline.py (z.B. für OpenCV cv2.error)?
2. Wird die Immutabilitätsregel verletzt? (Wird der Zustand halboffen gespeichert, bevor ein Schritt fehlerfrei endet?)
3. Fehlen Short-Circuits (Abbruch bei Reject)?
Sei direkt, schonungslos aber konstruktiv. Zeige immer an, wie es stattdessen gelöst werden muss.
"""

# Client mit dem neuen SDK initialisieren
client = genai.Client(api_key=api_key)

# Prompt zusammenbauen
prompt = f"Hier ist der Git-Diff eines neuen Pull Requests. Führe ein kritisches Code-Review durch:\n\n{diff_content}"

# Review generieren
response = client.models.generate_content(
    model='gemini-1.5-flash',
    contents=prompt,
    config=types.GenerateContentConfig(
        system_instruction=system_instruction,
    )
)

# Review in temporäre Datei schreiben für GitHub CLI
with open("review_output.txt", "w") as f:
    f.write(response.text)

# Review als Kommentar in den PR posten
subprocess.run([
    "gh", "pr", "comment", pr_number,
    "-F", "review_output.txt"
])
