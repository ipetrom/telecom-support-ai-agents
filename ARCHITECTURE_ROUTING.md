# RouterAgent vs FallbackAgent — Architektura

## Szybkie Porównanie

| Aspekt | **RouterAgent** | **FallbackAgent** |
|--------|-----------------|-------------------|
| **Kiedy uruchamiany** | Na KAŻDĄ wiadomość użytkownika | Tylko gdy router zgłosi `route="fallback"` |
| **Główna rola** | Wstępna klasyfikacja intencji | Prośba o wyjaśnienie |
| **Typ klasyfikacji** | LLM-based (semantic) | Nie klasyfikuje — zawsze prosi |
| **Wymaga LLM** | ✅ Tak | ❌ Nie |
| **Odpowiedzialność** | Routing do właściwego agenta | Obsługa niejasnych/out-of-scope |
| **Return value** | `{"route": "technical"\|"billing"\|"fallback", ...}` | `{"reply": "...", "route_hint": None}` |
| **Confidence** | ✅ Zwraca confidence score | ❌ Nie zwraca |
| **Przykład użycia** | "internet down" → route="technical" | "hello" → route="fallback" (asks for clarification) |

## Flow Rozmowy

```
┌─────────────────────────────────────┐
│    Użytkownik wysyła wiadomość      │
└──────────────┬──────────────────────┘
               │
               ▼
         ┌──────────────┐
         │ RouterAgent  │ ← LLM klasyfikuje intent
         │   (NEW!)     │
         └──────┬───────┘
                │
       ┌────────▼────────┐
       │ classification  │
       │ + confidence    │
       └────────┬────────┘
                │
        ┌───────▼────────────┐
        │ confidence >= 0.7? │
        └───────┬────────┬───┘
                │        │
              TAK      NIE
                │        │
                ▼        ▼
        ┌──────────┐  ┌─────────────────┐
        │ Route    │  │ route =         │
        │ to       │  │ "fallback"      │
        │ Specialist   └─────────┬───────┘
        │ Agent    │            │
        └──────────┘            ▼
                          ┌──────────────┐
                          │ FallbackAgent│
                          │   (ask)      │
                          └──────────────┘
```

## Szczegółowy Flow

### Scenario 1: Wiadomość z jasnym intencją (technical)

```python
# Wejście
user_message = "Moja sieć nie działa"

# RouterAgent
router.route(state, user_message)
→ {
    "route": "technical",
    "confidence": 0.95,
    "classification": {
        "category": "technical",
        "confidence": 0.95,
        "reasoning": "User reports network connectivity issue"
    }
  }

# Wynik: → TechnicalAgent otrzymuje wiadomość
```

### Scenario 2: Wiadomość z niejasnym intencją

```python
# Wejście
user_message = "Hello"

# RouterAgent
router.route(state, user_message)
→ {
    "route": "fallback",
    "confidence": 0.5,
    "classification": {
        "category": "unknown",
        "confidence": 0.5,
        "reasoning": "Greeting - insufficient context"
    }
  }

# Wynik: → FallbackAgent otrzymuje wiadomość
# FallbackAgent.run(state, "Hello")
# → {"reply": "I'm a specialist in technical support...", "route_hint": None}
```

### Scenario 3: Wiadomość z niskim confidence

```python
# Wejście
user_message = "Co robisz w czwartek?" (ambiguous)

# RouterAgent
router.route(state, user_message)
→ {
    "route": "fallback",  # confidence < 0.7
    "confidence": 0.3,
    "classification": {...}
  }

# Wynik: → FallbackAgent prosi o wyjaśnienie
```

## Architektura systemu (LangGraph)

```
┌─ graph.py ────────────────────────────────────┐
│                                                │
│  input_node                                    │
│      ↓                                         │
│  [router_node] ← RouterAgent (LLM)            │
│      ├─ route="technical" ──→ [tech_node]     │
│      ├─ route="billing" ────→ [billing_node]  │
│      └─ route="fallback" ───→ [fallback_node] │
│                                                │
│  [fallback_node] ← FallbackAgent              │
│      └─ (asks for clarification)              │
│                                                │
└────────────────────────────────────────────────┘
```

## Inicjalizacja w graph.py (przykład)

```python
from langchain_openai import ChatOpenAI
from router.router_agent import RouterAgent
from agents.fallback_agent import FallbackAgent
from agents.technical_agent import TechnicalAgent
from agents.billing_agent import BillingAgent

# Initialize LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Initialize agents
router = RouterAgent(llm=llm)  # ← Wymaga LLM
fallback = FallbackAgent()      # ← Nie wymaga LLM
technical = TechnicalAgent(...)
billing = BillingAgent(...)

# Router node
def router_node(state):
    result = router.route(state, state.messages[-1].content)
    
    if result["route"] == "technical":
        return {"next_agent": "technical"}
    elif result["route"] == "billing":
        return {"next_agent": "billing"}
    else:
        return {"next_agent": "fallback"}
```

## Edgecases

### Edge case 1: RouterAgent nie dostępny (LLM down)

**Opcja 1: Fallback heuristics** (zalecane)
```python
try:
    result = router.route(state, user_message)
except Exception as e:
    # Fallback to keyword-based routing
    result = keyword_based_route(user_message)
```

**Opcja 2: Zawsze to fallback**
```python
try:
    result = router.route(state, user_message)
except Exception:
    result = {"route": "fallback"}
```

### Edge case 2: Dwuznaczna wiadomość

```python
# "Why is my plan so expensive?" - mogą być oba: billing lub complaint
# RouterAgent: 
# confidence = 0.6 (ambiguous)
# → route = "fallback" (prośba o wyjaśnienie)
```

## Performance Considerations

| Aspekt | RouterAgent | FallbackAgent |
|--------|-------------|---------------|
| **Latency** | +200-500ms (LLM call) | <1ms (heuristics) |
| **Accuracy** | 90-95% (semantic) | 60-70% (keyword) |
| **Cost** | ~$0.0001 per call | $0 |
| **Reliability** | Zależy od LLM | 100% (deterministic) |

## Zalecenia

✅ **Kiedy używać RouterAgent:**
- Chcesz wysoką dokładność routowania
- Obsługujesz multi-lingual queries
- Masz budżet na LLM calls

✅ **Kiedy używać FallbackAgent:**
- Obsługa niejasnych/out-of-scope queries
- Polite clarification
- Zawsze po stronie RouterAgent (fallback)

## Przyszłe Rozszerzenia

1. **Caching confidence scores** — oszczędź LLM calls
2. **A/B testing** — porównaj keyword-based vs LLM-based routing
3. **Custom intents** — dodaj nowe kategorie (e.g., "account", "complaints")
4. **Feedback loop** — ucz LLM na misrouted examples
