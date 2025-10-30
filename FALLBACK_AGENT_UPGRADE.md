# FallbackAgent — Upgrade do LLM-Based Intent Classification

## Podsumowanie zmian

Zaktualizowałem `agents/fallback_agent.py` z sztywnej klasyfikacji słów kluczowych na **inteligentną klasyfikację intencji bazującą na LLM**. Teraz agent potrafi zrozumieć synonimów i różne warianty sformułowania pytań użytkownika.

## Poprzednia implementacja (słowa kluczowe)

```python
# Stara metoda — sztywna, wrażliwa na synonimów
tech_kw = ["wifi", "wi-fi", "apn", "pon", "router", ...]
bill_kw = ["invoice", "faktura", "refund", ...]

if any(k in t for k in tech_kw):
    return "technical"
```

**Problemy:**
- ❌ Nie rozumie synonimów (np. "moja sieć słaba" ≠ "internet")
- ❌ Wrażliwa na dodatkowe słowa
- ❌ Brak zaufania do klasyfikacji
- ❌ Nie obsługuje kontekstu

## Nowa implementacja (LLM-based)

```python
def _classify_intent(self, user_message: str) -> Dict[str, Any]:
    # Używa LLM do semantycznej analizy
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_message)
    ]
    response = self.llm.invoke(messages)
    # Zwraca: {"category": "technical"|"billing"|"unknown", 
    #          "confidence": 0.0-1.0, "reasoning": "..."}
```

**Zalety:**
- ✅ Rozumie synonimów i warianty sformułowania
- ✅ Wspiera wiele języków (PL, EN, etc.)
- ✅ Zwraca wynik zaufania (confidence score)
- ✅ Kontekstowa analiza intencji
- ✅ Łatwe do rozszerzenia o nowe kategorie

## Obsługiwane intencje

### 1. **technical** — Problemy techniczne
Przykłady (wszystkie obsługiwane):
- "My internet is down"
- "Moja sieć jest słaba" (polska)
- "Router keeps rebooting"
- "Can't connect to Wi-Fi"
- "No 5G signal"
- "Problem z łącznością APN"

### 2. **billing** — Rozliczenia i płatności
Przykłady (wszystkie obsługiwane):
- "I need a refund"
- "Czy mogę zwrócić pieniądze?"
- "Why was I charged twice?"
- "What's my invoice for?"
- "Ile kosztuje plan?"

### 3. **unknown** — Niejasne/nieznane
Przykłady:
- "Tell me a joke"
- "Hello"
- "Who are you?"

## Użycie

### Inicjalizacja

```python
from langchain_openai import ChatOpenAI
from agents.fallback_agent import FallbackAgent

# Utwórz LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Utwórz agenta z LLM
agent = FallbackAgent(llm=llm)
```

### Uruchomienie

```python
from agents.fallback_agent import ConversationState

state = ConversationState()
result = agent.run(state, "Moja sieć nie działa")

# Zwraca:
# {
#     "reply": "I understand you have a technical issue...",
#     "route_hint": "technical",  # lub "billing" | None
#     "confidence": 0.92,          # zaufanie (0.0-1.0)
#     "classification": {...}      # pełne detale klasyfikacji
# }
```

## Logika routowania

```
Jeśli confidence >= 0.7 i route_hint ∈ ["technical", "billing"]:
    ✅ Wysłanie do odpowiedniego agenta + potwierdzenie
Else:
    ❓ Prośba o wyjaśnienie (ask for clarification)
    route_hint = None
```

## Nowe funkcje w API

| Funkcja | Opis |
|---------|------|
| `FallbackAgent(llm)` | Inicjalizacja z LLM (wymagane) |
| `run(state, user_message)` | Klasyfikacja i routowanie |
| `_classify_intent(user_message)` | LLM-based klasyfikacja (zwraca dict) |
| `_get_confirmation_message(route_hint, user_message)` | Kontekstowe potwierdzenie |

## Struktura odpowiedzi (return value)

```json
{
  "reply": "string (komunikat dla użytkownika)",
  "route_hint": "technical | billing | null",
  "confidence": 0.0-1.0,
  "classification": {
    "category": "technical | billing | unknown",
    "confidence": 0.0-1.0,
    "reasoning": "string (wyjaśnienie decyzji)"
  }
}
```

## Testowanie

Nowy plik testowy: `tests/test_fallback_agent_llm.py`

```bash
python tests/test_fallback_agent_llm.py
```

**Testy obejmują:**
- ✅ Słowa kluczowe bezpośrednie (technical, billing)
- ✅ Synonimów (PL i EN)
- ✅ Warianty rozmowne
- ✅ Niejasne intencje
- ✅ Kontekstowe analizy

## Konfiguracja systemu LLM

System prompt zawiera:
- Szczegółowy opis każdej kategorii
- Liczne przykłady w każdym języku
- Reguły elastyczności i synonymów
- Format oczekiwanej odpowiedzi JSON

## Wymagania

- `langchain>=0.2.0`
- `langchain-openai>=0.1.0`
- `openai>=1.40.0`

(Już w `requirements.txt`)

## Migracja z poprzedniej wersji

### Stary kod:
```python
agent = FallbackAgent()
result = agent.run(state, "user message")
# result: {"reply": "...", "route_hint": "technical" | "billing" | None}
```

### Nowy kod:
```python
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
agent = FallbackAgent(llm=llm)  # ← LLM jest teraz wymagany
result = agent.run(state, "user message")
# result: {"reply": "...", "route_hint": "...", "confidence": 0.92, "classification": {...}}
```

## Następne kroki (opcjonalne)

1. **Integracja z graph.py** — zaktualizuj węzły routowania aby używały nowego agenta
2. **Monitorowanie confidence** — śledź zdarzenia z niskim zaufaniem dla poprawy systemu
3. **Dodatkowe kategorie** — rozszerz intencje (np. "account", "technical", "billing", "general")
4. **Fine-tuning** — dostosuj system prompt do specyficznych potrzeb

## Troubleshooting

**P: Agent zawsze zwraca confidence < 0.7?**
A: Sprawdź czy LLM prawidłowo parsuje JSON. Dodaj logging w `_classify_intent()`.

**P: Błedy JSON od LLM?**
A: Kod zawiera fallback na `unknown` przy JSONDecodeError. Spróbuj inny model (np. gpt-4).

**P: Jak obsługiwać więcej języków?**
A: System prompt już wspiera PL/EN. Dodaj więcej przykładów do prompt'u.
