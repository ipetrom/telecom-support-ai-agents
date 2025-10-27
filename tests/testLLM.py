import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(override=False)  # nie nadpisuj już ustawionych zmiennych

key = os.getenv("OPENAI_API_KEY", "").strip()
# Walidacja – blokada na placeholdery
if not (key.startswith("sk-") and "your" not in key.lower()):
    raise RuntimeError(f"Nieprawidłowy OPENAI_API_KEY (prefix: {key[:10] if key else '(empty)'}).")

client = OpenAI(api_key=key)

resp = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role":"user","content":"Napisz jedno zdanie: Test połączenia działa."}],
    temperature=0
)
print(resp.choices[0].message.content.strip())