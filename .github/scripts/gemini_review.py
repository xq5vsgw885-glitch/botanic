import os
import subprocess
from google import genai
from google.genai import types

api_key = os.environ.get("GEMINI_API_KEY")
pr_number = os.environ.get("PR_NUMBER")

try:
    with open("pr_diff.txt", "r") as f:
        diff_content = f.read()
except FileNotFoundError:
    diff_content = ""

if not diff_content.strip():
    print("Keine Änderungen zum Reviewen.")
    exit(0)

system_instruction = """
Du bist der leitende kritische Code-Reviewer für eine botanische Computer-Vision-Pipeline.
1. Fehlen globale Exception-Catcher in der pipeline.py (z.B. für OpenCV cv2.error)?
2. Wird die Immutabilitätsregel verletzt?
3. Fehlen Short-Circuits (Abbruch bei Reject)?
"""

client = genai.Client(api_key=api_key)
prompt = f"Hier ist der Git-Diff eines neuen Pull Requests. Führe ein kritisches Code-Review durch:\n\n{diff_content}"

response = client.models.generate_content(
    model='gemini-1.5-flash',
    contents=prompt,
    config=types.GenerateContentConfig(
        system_instruction=system_instruction,
    )
)

with open("review_output.txt", "w") as f:
    f.write(response.text)

subprocess.run(["gh", "pr", "comment", pr_number, "-F", "review_output.txt"])
