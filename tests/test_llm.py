import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(override=False)  # nie nadpisuj już ustawionych zmiennych

key = os.getenv("OPENAI_API_KEY")
if not key:
    raise RuntimeError("OPENAI_API_KEY nie ustawiony")

client = OpenAI(api_key=key)
resp = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role":"user", "content":"Napisz jedno zdanie: Test połączenia działa."}],
    temperature=0
)
print(resp.choices[0].message.content.strip())
