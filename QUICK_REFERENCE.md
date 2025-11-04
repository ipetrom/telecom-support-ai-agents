# Telecom Support AI Agents - Quick Reference Guide

## Project Overview

A production-ready **multi-agent LLM system** for telecom customer support with zero-hallucination guarantees.

---

## Architecture at a Glance

```
FastAPI /chat endpoint
    ↓
Session State Management
    ↓
LangGraph State Machine
    ├─ Router Node (LLM intent classification)
    └─ Conditional routing to:
       ├─ Technical Agent (RAG + FAISS retrieval)
       ├─ Billing Agent (Tool calling)
       └─ Fallback Agent (Clarification)
    ↓
Return response + sources + audit trail
```

---

## Key Components

### 1. **Data Pipeline (RAG Preparation)**

**What happens:**
- Load Markdown docs from `data/docs/`
- Extract YAML front matter (title, version, section paths)
- Normalize text (remove HTML, collapse lines)
- Chunk with `RecursiveCharacterTextSplitter` (600 tokens, 120 overlap)
- Embed with OpenAI `text-embedding-3-small` (1536 dims)
- Build FAISS index in `artifacts/`

**Files involved:**
- `retriever/build_vectorstore.py` — Build pipeline
- `data/docs/01-04_*.md` — Knowledge base
- `artifacts/` — FAISS index + metadata

**Key concept:** **Semantic chunking respects document structure** (headers, lists) to avoid mid-thought breaks.

---

### 2. **Retrieval Architecture**

**Query → Retrieval → Sources**

Steps:
1. **Embed query** (OpenAI embedding)
2. **MMR search** (Max Marginal Relevance) → diverse candidates, not just similar
3. **Dedup** by (doc_id, section_path) → keep highest-scoring per section
4. **Score evaluation** → NO_CONTEXT if <0.5 avg score or <3 hits
5. **Return** top-8 chunks with sources

**Hallucination guard:** If NO_CONTEXT → TechnicalAgent asks for clarification instead of answering.

**Files involved:**
- `retriever/retriever.py` — KBRetriever class

---

### 3. **Router Agent (Intent Classification)**

**"What does the user want?"**

LLM-based classification:
- **technical** — internet, Wi-Fi, router, APN, bridge, 5G/DSL/FTTH, etc.
- **billing** — invoices, refunds, plans, pricing, payment status
- **unknown** — ambiguous or out-of-scope

**Smart routing logic:**
- High confidence (>70%) + clear category → Route to specialist
- Low confidence + recent context → Stay with current agent (avoid jarring switches)
- <50% confidence → Route to FallbackAgent

**Files involved:**
- `agents/router_agent.py`

---

### 4. **Technical Agent (Grounded RAG Responses)**

**"Answer using ONLY the knowledge base."**

Workflow:
1. Retrieve docs via KBRetriever
2. If NO_CONTEXT → Ask for clarification
3. Else → Build LLM prompt with retrieved docs
4. LLM generates response
5. Append mandatory Sources section
6. Return response + sources + scores

**Hallucination guarantees:**
- ✅ System prompt forbids inventing facts
- ✅ NO_CONTEXT threshold enforced
- ✅ Sources mandatory (auto-appended if missing)
- ✅ Context budget capped at 8KB

**Files involved:**
- `agents/technical_agent.py`

---

### 5. **Billing Agent (Tool-Calling Specialist)**

**"Call tools to get/create deterministic billing data."**

Available tools:
1. `get_subscription(user_id)` → Plan, price, status
2. `open_refund_case(user_id, reason, amount_pln, invoice_id, description)` → Create case
3. `get_refund_policy()` → Return policy details

**Tool-calling workflow:**
1. LLM sees tools + user message
2. LLM calls tool (e.g., `open_refund_case`)
3. Tool executes (Pydantic validation, in-memory store)
4. Result fed back to LLM
5. LLM generates final summary response

**Hallucination guarantee:** LLM cannot invent prices—only call `get_subscription()`.

**Files involved:**
- `agents/billing_agent.py`
- `tools/billing_tools.py`

---

### 6. **Fallback Agent (Polite Clarification)**

**"Hmm, I'm not sure. Can you clarify?"**

When routing is ambiguous (confidence <50%):
- Show template: "I can help with [TECH] / [BILLING] / [OTHER]"
- Infer weak route hint (keyword-based)
- Next turn: Router re-evaluates (no commitment to hint)

**Files involved:**
- `agents/fallback_agent.py`

---

### 7. **State Management & Multi-Turn Conversations**

**Conversation memory:**
- Entire conversation stored in `state["history"]`
- Each turn appends `{role: "user"|"assistant", content: str}`
- Multi-turn flows naturally (context preserved)

**Session persistence:**
```python
AppState.sessions[session_id] = state
```

**Bounded history** (prevent token overflow):
- TechnicalAgent: Uses full history (typically short)
- BillingAgent: Keeps last 12 messages (6 turns)

**Easy to persist:** Replace `AppState.sessions` dict with database.

**Files involved:**
- `main.py` — FastAPI + session management
- `graph.py` — State definitions

---

## Hallucination Prevention (5 Layers)

1. **NO_CONTEXT Threshold** → Retriever rejects weak results (<0.5 score)
2. **Source Citation** → Every claim must be attributed (auto-appended)
3. **System Prompts** → LLM explicitly told: "Don't invent facts"
4. **Tool Calling** → Billing agent can't hallucinate (tools return real data)
5. **Input Validation** → Pydantic schemas reject malformed tool calls

---

## Complete Request Flow (Example)

**User:** "My router PON LED is blinking red. What's wrong?"

1. **Router** classifies as "technical" (confidence 0.95)
2. **Retriever** searches FAISS → finds 8 relevant chunks (avg score 0.78)
3. **NO_CONTEXT check** passes (0.78 > 0.5, 8 >= 3)
4. **TechnicalAgent** builds context block + LLM prompt
5. **LLM** generates response using docs
6. **Sources appended** automatically
7. **Response returned** with sources + scores
8. **State saved** with conversation history

**Total time:** ~1-2 seconds (one LLM call + one embedding call)

---

## File Structure

```
.
├── main.py                          # FastAPI app + session management
├── graph.py                         # LangGraph state machine
├── agents/
│   ├── router_agent.py              # Intent classification
│   ├── technical_agent.py           # RAG specialist
│   ├── billing_agent.py             # Tool-calling specialist
│   └── fallback_agent.py            # Clarification
├── retriever/
│   ├── build_vectorstore.py         # Build FAISS index
│   └── retriever.py                 # Query retriever
├── tools/
│   └── billing_tools.py             # Billing functions + tool wrappers
├── data/
│   └── docs/                        # Knowledge base (Markdown)
├── artifacts/                       # FAISS index + metadata
├── tests/                           # Test files
├── requirements.txt
└── SYSTEM_ARCHITECTURE.md           # Full documentation
```

---

## Key Configuration

### Environment Variables

```bash
OPENAI_API_KEY=sk-...                   # Required
MODEL_NAME=gpt-4o-mini                  # LLM model
EMBEDDING_MODEL=text-embedding-3-small  # Embedder
```

### Retriever Config

```python
RetrieverConfig(
    top_k=8,              # Final results
    fetch_k=24,           # Candidates before dedup
    threshold=0.5,        # NO_CONTEXT cutoff
    min_hits=3,           # Min chunks required
    lambda_mult=0.7       # MMR diversity
)
```

### LangGraph Nodes

```
START → router → [technical | billing | fallback] → END
```

---

## Deployment (FastAPI)

```bash
# Start server
uvicorn main:app --reload --port 8000

# Make request
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "user_123",
    "user_id": "u456",
    "message": "My internet is down"
  }'

# Response
{
  "reply": "Based on the knowledge base...",
  "route": "technical",
  "last_agent": "technical",
  "sources": [
    {"title": "Router LED Indicators", "section": "Troubleshooting", ..., "score": 0.82},
    ...
  ],
  "used_tools": null,
  "state_excerpt": {"last_agent": "technical", "history_length": 2}
}
```

---

## Key Design Principles

✅ **Explicit state** (no hidden context in LLM)
✅ **Semantic routing** (LLM-based, handles synonyms + Polish/English)
✅ **RAG for grounding** (prevent hallucination via NO_CONTEXT)
✅ **Tools for verification** (deterministic billing answers)
✅ **Multi-turn awareness** (avoid jarring agent switches)
✅ **Bounded token usage** (history truncation, context budget)
✅ **Production-ready** (Pydantic validation, error handling, audit trails)

---

## Testing

```bash
# Smoke tests
pytest tests/test_router_agent.py
pytest tests/test_technical_agent.py
pytest tests/test_billing_agent.py
pytest tests/test_fallback_agent.py

# RAG pipeline
pytest tests/test_rag.py

# Embeddings
pytest tests/test_embeddings.py
```

---

## Next Steps

1. **Replace mock data** in `billing_tools.py` with real API/database
2. **Add more documents** to `data/docs/` (auto-indexed on restart)
3. **Integrate with CRM** for user context
4. **Persist sessions** to Redis/PostgreSQL
5. **Add monitoring** (LLM call costs, response times, failure rates)
6. **Scale horizontally** (containerize with Docker, deploy to Kubernetes)

---

**See `SYSTEM_ARCHITECTURE.md` for complete details.**
