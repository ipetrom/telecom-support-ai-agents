# Telecom Support AI Agents - Complete System Architecture

**A production-ready multi-agent system for intelligent customer support using LangGraph, RAG, and LLM-based routing.**

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Data Preparation & Vector Store (RAG Pipeline)](#data-preparation--vector-store-rag-pipeline)
3. [Retrieval Architecture](#retrieval-architecture)
4. [Multi-Agent Orchestration](#multi-agent-orchestration)
5. [Agent Implementations](#agent-implementations)
6. [Conversation State & Memory Management](#conversation-state--memory-management)
7. [Hallucination Prevention & Safeguards](#hallucination-prevention--safeguards)
8. [Complete Request Flow](#complete-request-flow)
9. [Key Design Principles](#key-design-principles)

---

## Executive Summary

The **Telecom Support AI Agents** system is a sophisticated multi-agent architecture designed to handle customer support queries with **semantic understanding** and **zero hallucination guarantees** for technical documentation.

**Key features:**
- **Intelligent routing** via LLM-based intent classification (technical, billing, or fallback)
- **Grounded technical responses** using RAG (Retrieval-Augmented Generation) with FAISS
- **Tool-calling billing agent** for subscription and refund management
- **Hallucination prevention** through NO_CONTEXT thresholds and source citation enforcement
- **Multi-turn conversation support** with persistent state management
- **FastAPI REST API** for seamless integration

**Tech stack:**
- **LLM**: OpenAI GPT-4o-mini
- **Orchestration**: LangGraph (state machine + conditional routing)
- **RAG**: FAISS vector database + OpenAI embeddings (text-embedding-3-small)
- **Tool framework**: LangChain StructuredTool
- **Backend**: FastAPI with CORS support

---

## Data Preparation & Vector Store (RAG Pipeline)

### Step 1: Document Loading & Front Matter Extraction

**File**: `retriever/build_vectorstore.py`

The system ingests Markdown documents from `data/docs/` with optional YAML front matter:

```markdown
---
title: "Wi-Fi Connectivity Troubleshooting"
version: "2.1"
last_updated: "2025-10-15"
audience: "end_users"
language: "en"
summary: "Step-by-step guide to resolve Wi-Fi connectivity issues on 2.4GHz and 5GHz bands"
---

# Content starts here...
```

**Extraction logic:**
- Regex-based front matter parsing (`FRONT_MATTER_RE`)
- YAML deserialization for structured metadata
- Fallback handling if front matter is absent or malformed
- Metadata fields: `title`, `version`, `last_updated`, `audience`, `language`, `summary`

### Step 2: Text Normalization

**Purpose**: Clean and standardize markdown without destroying semantic structure

**Transformations:**
- Table conversion to plain text (preserve content, remove pipe formatting)
- HTML comment removal
- Collapse excessive blank lines (>2) to 2 lines
- Trim trailing whitespace
- **Preserve**: Headers (`#`), lists, code blocks—these are semantic boundaries

**Result**: Clean, normalized markdown ready for semantic chunking.

### Step 3: Intelligent Chunking

**Algorithm**: `RecursiveCharacterTextSplitter` with hierarchical separators

**Configuration:**
- `chunk_size`: 600 tokens (default)
- `chunk_overlap`: 120 tokens (20% overlap for context continuity)
- **Separator hierarchy**: 
  ```
  "\n## " (H2 headers)
    → "\n### " (H3 headers)
    → "\n- " (bullet lists)
    → "\n1) " (numbered lists)
    → "\n" (newlines)
    → " " (word boundaries)
  ```

**Why this order?**
- Respects logical document structure (chapters → sections → subsections)
- Avoids mid-sentence breaks
- Captures complete procedural steps or conceptual units

**Quality filter:** Chunks <200 tokens **and** lacking any document keywords are discarded (too low information density).

**Example chunk:**
```
[H2: Router LED Indicators]
PON LED (green/red/blinking):
- Green: Active connection, healthy
- Red: No signal detected
- Blinking: Synchronizing with ONT
[H3: Troubleshooting]
1) Check cable integrity...
```

### Step 4: Section Path Inference

**Purpose**: Extract hierarchical context for each chunk

**Logic:**
- Scan the full document up to the chunk's position
- Extract all header levels (count of `#`)
- Keep the last 3 headers as "section path"
- Example result: `["Internet Setup", "ONT Configuration", "Bridge Mode"]`

**Why?** Enables semantic citation: "Title — Section → Subsection — File (v2.1)"

### Step 5: Metadata Enrichment & Keyword Extraction

**Per-chunk metadata:**
```python
Chunk(
    doc_id="01_troubleshooting_internet",
    title="Troubleshooting Internet Connection",
    section_path=["Common Issues", "No Internet"],
    path="data/docs/01_troubleshooting_internet.md",
    version="2.1",
    last_updated="2025-10-15",
    audience="end_users",
    keywords=["internet", "offline", "router", "pon", "led", ...],
    language="en",
    text="...",
    sha1="<hash>"  # content fingerprint
)
```

**Keyword extraction:**
- Source: document summary + all header titles
- Normalized to lowercase, stripped punctuation
- Length filter: 2 < word_length < 24
- Deduped and limited to top 12 keywords
- **Purpose**: Quick relevance filtering, audit trails

### Step 6: Embedding Generation & FAISS Indexing

**Embedder**: OpenAI `text-embedding-3-small` (1536 dimensions)

**Process:**
1. Convert each chunk's text to embedding via OpenAI API
2. Batch embeddings into FAISS index
3. Save index + embedder metadata to `artifacts/` directory

**FAISS artifacts:**
```
artifacts/
├── index.faiss              # Vector index (serialized)
├── index.pkl                # FAISS index metadata
├── embedder_info.json       # Embedder model + config
├── index_meta.json          # Chunk metadata (doc_id, section_path, etc.)
└── stats.json               # Index statistics (min/max/avg scores)
```

**Index statistics** (optional, computed for monitoring):
- Cosine similarity distribution across index
- Percentile scores (p10, p25, p50, p75, p90)
- Used to calibrate NO_CONTEXT threshold dynamically

---

## Retrieval Architecture

### Retriever Configuration

**File**: `retriever/retriever.py` — `RetrieverConfig` dataclass

```python
@dataclass
class RetrieverConfig:
    artifacts_dir: Path = Path("artifacts")
    top_k: int = 8              # Final results returned
    fetch_k: int = 24           # Candidates fetched before dedup/rerank
    threshold: float = 0.5      # Cosine similarity NO_CONTEXT cutoff
    min_hits: int = 3           # Minimum chunks required for confidence
    lambda_mult: float = 0.7    # MMR diversity factor (0.0=pure relevance, 1.0=pure diversity)
    freshness_boost: float = 0.0  # Disabled: prevented NO_CONTEXT detection
    step_section_boost: float = 0.0  # Disabled: same reason
```

### MMR-Based Retrieval Pipeline

**Step 1: Query Embedding**
- User query → OpenAI embedder → 1536-dim vector

**Step 2: Max Marginal Relevance (MMR) Fetch**
```python
mmr_docs = vs.max_marginal_relevance_search(
    query, 
    k=fetch_k,  # Get top 24 candidates
    lambda_mult=0.7  # Balance relevance vs. diversity
)
```

**What is MMR?**
- Mathematical goal: `argmax_D [λ·sim(q,d) - (1-λ)·max_d'∈D sim(d,d')]`
- **Relevance term**: How similar is document `d` to query `q`?
- **Diversity term**: How different is `d` from already-selected documents?
- **Lambda (0.7)**: 70% weight on relevance, 30% on diversity
- **Result**: Avoid returning 10 nearly-identical chunks; return varied perspectives

**Step 3: Score Lookup & Deduplication**

```python
scored_candidates = vs.similarity_search_with_score(query, k=fetch_k)
# Build score_map: {doc_id|section_path → cosine_score}
```

**Dedup logic:** Keep only the highest-scoring chunk per unique `(doc_id, section_path)` pair
- **Why?** Prevent redundancy: two very similar chunks from same section are redundant
- **Preserve order**: MMR order maintained (best-first)

**Step 4: Optional Boosts (Currently Disabled)**

Originally included:
- **Freshness boost**: Prioritize recently-updated docs
- **Step section boost**: Boost procedural sections (containing "step", "verification")

**Disabled because**: These boosted scores above 1.0, breaking the 0.5 threshold logic. Prefer explicit query design (e.g., "step-by-step guide" in query) to implicit boosting.

**Step 5: Top-K Truncation**

Select top 8 chunks from deduped, scored results.

### NO_CONTEXT Threshold Decision

**Critical safeguard:** When does the retriever declare "insufficient context"?

```python
no_context = (len(items) < min_hits) or (mean_score < threshold)
```

**Conditions:**
- **Fewer than 3 chunks** retrieved → NO_CONTEXT = True
- **OR average cosine similarity < 0.5** → NO_CONTEXT = True

**Outcome if NO_CONTEXT:**
- TechnicalAgent asks for clarification instead of hallucinating
- Requests specific details: device model, access type (FTTH/DSL/LTE/5G), symptoms
- Mentions what's missing from the knowledge base

**Example:**
```
Query: "my network is broken"
Retrieved: [low-similarity generic docs]
Mean score: 0.35 < 0.5 threshold
→ NO_CONTEXT = True
→ TechnicalAgent response: "I couldn't find enough info. Please clarify: 
   device model, access type, and specific symptoms (e.g., PON LED behavior)."
```

### Source Citation

**Each retrieved chunk is tagged with:**
```python
{
    "title": "Wi-Fi Connectivity Guide",
    "section": "Troubleshooting / LED Indicators",
    "file": "02_router_wifi.md",
    "version": "2.1",
    "score": 0.8234
}
```

**TechnicalAgent appends:**
```
Sources:
- Wi-Fi Connectivity Guide — Troubleshooting / LED Indicators — 02_router_wifi.md (2.1)
- Router Setup — Bridge Mode Config — 03_apn_bridge.md (1.0)
```

---

## Multi-Agent Orchestration

### LangGraph Architecture

**File**: `graph.py`

The system uses **LangGraph** (LangChain's state machine library) to orchestrate multi-agent workflows.

**Why LangGraph?**
- Explicit state management (no hidden context passing)
- Deterministic routing logic (easy to debug, reproduce)
- Conditional edges (router decision branches to specialist nodes)
- Serializable execution (can pause, resume, or audit)

### GraphState Definition

```python
class GraphState(TypedDict, total=False):
    history: List[Dict[str, str]]          # Multi-turn conversation
    user_id: Optional[str]                 # For billing context
    last_agent: Optional[str]              # 'technical', 'billing', or 'fallback'
    context_flags: Dict[str, Any]          # Transient state flags
    last_docs: List[Dict[str, Any]]        # Audit trail: last sources
    route: str                             # Current routing decision
    reply: str                             # Agent's response
```

**Key insight:** All state is **explicit and serializable**. No hidden LLM context or implicit globals.

### Execution Flow

```
START
  ↓
┌────────────────────┐
│  ROUTER NODE       │
│  • Last user msg   │
│  • Intent classification (LLM)
│  • Returns: route ∈ {"technical", "billing", "fallback"}
└────────┬───────────┘
         │
    ┌────┴──────────────┬──────────────┐
    │                   │              │
    ▼                   ▼              ▼
┌──────────┐  ┌──────────┐  ┌──────────┐
│TECHNICAL │  │ BILLING  │  │FALLBACK  │
│ (RAG)    │  │ (tools)  │  │(clarify) │
└────┬─────┘  └────┬─────┘  └────┬─────┘
     │             │             │
     └─────────┬───┴─────────────┘
               │
               ▼
             END
             (Reply stored in state)
```

**One-turn execution**: Router → Specialist → END

**Multi-turn handling**: FastAPI loop calls `run_turn()` repeatedly, passing state through.

---

## Agent Implementations

### 1. Router Agent (Smart Intent Classification)

**File**: `agents/router_agent.py`

**Purpose**: Every incoming message is classified to determine which specialist handles it.

**Classification categories:**
1. **technical**: Internet, Wi-Fi, router, APN, bridge mode, ONT, 5G/DSL/FTTH, connectivity issues
   - Examples: "internet drops", "Wi-Fi won't connect", "moja sieć słaba"
2. **billing**: Invoices, payments, subscriptions, refunds, pricing, account status
   - Examples: "why was I charged?", "ile kosztuje plan", "refund request"
3. **unknown**: Doesn't fit above or is ambiguous
   - Examples: "hello", "who are you?", "tell me a joke"

**System Prompt** (guides LLM classification):
```
You are an expert intent classifier for a telecom support system.
Categories:
1. technical — Internet, Wi-Fi, router, APN, bridge mode, 5G/DSL/FTTH, etc.
2. billing — Invoices, payments, subscriptions, refunds, pricing
3. unknown — Anything else or ambiguous

Rules:
- Be flexible with synonyms, slang, Polish/English mix
- Consider context and related terms
- If ambiguous, use "unknown"
- Always respond as valid JSON: {"category": "...", "confidence": 0.0-1.0, "reasoning": "..."}
```

**Routing Decision Logic** (sophisticated context-awareness):

```
IF confidence >= 0.7 AND category IN ["technical", "billing"]:
    IF state.last_agent IN ["technical", "billing"] AND has_recent_context:
        IF category == state.last_agent OR category == "unknown":
            route = state.last_agent  # Stay with current agent
        ELSE:
            route = category  # High confidence: switch
    ELSE:
        route = category  # Fresh start: route to classified agent
        
ELIF state.last_agent IN ["technical", "billing"] AND confidence < 0.7:
    route = state.last_agent  # Low confidence follow-up: stay
    
ELIF confidence >= 0.5 AND category IN ["technical", "billing"]:
    route = category  # Medium confidence: route to category
    
ELSE:
    route = "fallback"  # Low confidence or unknown: ask for clarification
```

**Key insight:** Conversation context matters. If you're already talking to TechnicalAgent and ask a vague follow-up question, stay with them rather than randomly routing.

**Context detection** (`_has_recent_agent_context`):
- Checks if last 4 messages contain an assistant reply
- Confirms we're in active conversation, not starting fresh

**Output:**
```python
{
    "route": "technical" | "billing" | "fallback",
    "confidence": 0.75,  # 0.0-1.0
    "classification": {
        "category": "technical",
        "confidence": 0.75,
        "reasoning": "User mentions internet and PON LED status"
    }
}
```

### 2. Technical Agent (Grounded RAG Responses)

**File**: `agents/technical_agent.py`

**Purpose**: Answer technical support questions using ONLY retrieved knowledge base.

**Workflow:**

```
User query
    ↓
Retrieve(query) → [docs], scores, no_context_flag
    ↓
IF no_context:
    Return: "Insufficient context. Please clarify: device model, access type, symptoms."
ELSE:
    Build LLM prompt with CONTEXT
    Send to LLM
    LLM generates response
    Append Sources section
    Return response + sources
```

**System Prompt**:
```
You are TechnicalAgent. Answer ONLY using the provided CONTEXT chunks.
If context is insufficient, ask for clarification.

Rules:
- Be concise and actionable
- Never invent facts beyond CONTEXT
- Always include 'Sources' section: Title — Section — File (version)
- If NO_CONTEXT: ask for 1-2 clarifying details and mention what's missing
```

**Context composition** (bounded to 8KB):
- Max 8000 characters of context
- Each source formatted as: `[SOURCE] Title — Section — File (version)\n<body>`
- Stop adding sources once 8KB budget exceeded
- Prevents token overflow and maintains efficiency

**LLM Invocation**:
```python
messages = [
    SystemMessage(content=SYSTEM_PROMPT),
    HumanMessage(content="""
    CONTEXT (from local KB):
    [SOURCE] Wi-Fi Connectivity — LED Indicators — 02_router_wifi.md (v2.1)
    <body>
    
    [SOURCE] Router Setup — Bridge Mode — 03_apn_bridge.md (v1.0)
    <body>
    
    QUESTION:
    My router's PON LED is blinking. What does this mean?
    
    Respond concisely. Always add 'Sources'.""")
]
response = llm.invoke(messages)
```

**Response cleanup**:
- If LLM omits "Sources:" section, append it automatically
- If LLM includes `[SOURCES]` placeholder, replace with actual sources
- **Goal**: Guarantee citation, no matter LLM behavior

**Return value**:
```python
{
    "reply": "PON LED blinking indicates synchronization in progress...\nSources:\n- ...",
    "sources": [
        {
            "title": "Wi-Fi Connectivity",
            "section": "LED Indicators",
            "file": "02_router_wifi.md",
            "version": "2.1",
            "score": 0.82
        },
        ...
    ],
    "no_context": False
}
```

**Hallucination prevention:**
- ✅ NO_CONTEXT threshold enforced by retriever
- ✅ Sources mandatory (appended if missing)
- ✅ LLM explicitly instructed: "ONLY using provided CONTEXT"
- ✅ No external knowledge attempted

### 3. Billing Agent (Tool-Calling Specialist)

**File**: `agents/billing_agent.py`

**Purpose**: Handle billing queries via structured tool calling.

**Available tools:**
1. `get_subscription(user_id)` — Fetch plan, price, status
2. `open_refund_case(user_id, reason, amount_pln, invoice_id, description)` — Create refund case
3. `get_refund_policy()` — Return policy (cooling-off, SLA, non-refundable items)

### Billing Tools Implementation

**File**: `tools/billing_tools.py`

**Mock data (MVP):**
```python
_USERS = {
    "u123": _Sub(plan_code="M", start_date=date(2025, 8, 15), status="active"),
    "u456": _Sub(plan_code="L", start_date=date(2025, 6, 1), status="active"),
}

_PLANS = {
    "S": _Plan(name="S 50 GB", monthly_price=35.0),
    "M": _Plan(name="M 100 GB", monthly_price=45.0),
    "L": _Plan(name="L Unlimited", monthly_price=65.0),
}
```

**Tool 1: `get_subscription(user_id) → SubscriptionOut`**

```python
def get_subscription(user_id: str) -> SubscriptionOut:
    sub = _USERS.get(user_id)
    if not sub:
        return SubscriptionOut(..., status="not_found")
    plan = _PLANS[sub.plan_code]
    return SubscriptionOut(
        user_id=user_id,
        plan_code=sub.plan_code,
        plan_name=plan.name,
        price_monthly_pln=plan.monthly_price,
        status=sub.status,
        start_date=sub.start_date
    )
```

**Tool 2: `open_refund_case(...) → RefundCaseOut`**

```python
def open_refund_case(
    user_id: str, 
    reason: RefundReason,  # overcharge, service_outage, within_cooling_off, other
    amount_pln: float,      # 0 < x ≤ 1000
    invoice_id: str,
    description: Optional[str]
) -> RefundCaseOut:
    case_id = f"R{next(_CASE_COUNTER)}"  # Auto-incremented: R10001, R10002, ...
    policy = get_refund_policy()
    
    # Validation: user exists?
    sub = _USERS.get(user_id)
    if not sub:
        return RefundCaseOut(
            case_id=case_id,
            status="pending_review",
            next_steps=["User not found. Verify user_id or create new subscription."],
            sla_business_days=policy.processing_sla_business_days,
            eta_date=date.today() + timedelta(days=5)
        )
    
    # Domain rules
    steps = [
        f"Case created for invoice {invoice_id}.",
        f"Classification: {reason.value}.",
        "Billing specialist will validate charge.",
        f"If approved: refund {amount_pln:.2f} PLN to original payment method."
    ]
    
    if reason == RefundReason.WITHIN_COOLING_OFF:
        steps.append("Cooling-off period applies (14 days). Priority processing.")
        status = "pending_review"
    else:
        status = "opened"
    
    return RefundCaseOut(
        case_id=case_id,
        status=status,
        next_steps=steps,
        sla_business_days=5,
        eta_date=date.today() + timedelta(days=5)
    )
```

**Tool 3: `get_refund_policy() → RefundPolicyOut`**

```python
class RefundPolicyOut(BaseModel):
    cooling_off_days: int = 14                    # 14-day withdrawal period
    processing_sla_business_days: int = 5         # 5 business days to process
    refund_to_method_days: str = "7-10"           # After approval, funds appear in 7-10 days
    non_refundable_items: List[str] = [
        "One-time activation fees after activation",
        "Usage outside plan (premium services)",
    ]
    notes: List[str] = [
        "Refunds issued to original payment method",
        "Business days exclude weekends and Polish holidays",
    ]
```

**Pydantic validation** (strict I/O):
- `RefundCaseIn` schema: Validates user_id, reason enum, amount range (>0, ≤1000), invoice_id format
- `SubscriptionOut`, `RefundCaseOut`: Typed responses with defaults
- Invalid inputs rejected before tool execution

### Billing Agent Execution

**System Prompt**:
```
You are BillingAgent, a precise billing specialist.

Scope: confirm subscription plan & price; explain refund policy; open refund cases.

Rules:
- Use tools when needed. Ask for missing fields (user_id, reason, amount, invoice_id).
- Keep answers concise (≤ 6 sentences) and list clear next steps.
- Currency is PLN. Do not invent data.
- If request is outside billing scope, say so briefly and return control to router.
```

**Workflow:**

```
User message: "I was overcharged PLN 100 on invoice INV-12345"
    ↓
LLM (with tools bound)
    ↓
Missing user_id → LLM response: "I found an overcharge claim. To proceed, I need your customer ID. What's your user ID?"
    ↓
User: "It's u123"
    ↓
LLM calls: open_refund_case(user_id="u123", reason="overcharge", amount_pln=100, invoice_id="INV-12345")
    ↓
Tool executes → case_id="R10001", status="opened", next_steps=[...]
    ↓
LLM summarizes: "Case R10001 has been opened. We'll validate your claim within 5 business days..."
```

**Tool calling mechanics** (LangChain):

```python
self.llm = llm.bind_tools(tools)  # Bind tools to LLM

messages = [SystemMessage(...), ...HumanMessage(...)]
ai = self.llm.invoke(messages)

if ai.tool_calls:
    for call in ai.tool_calls:
        name = call["name"]        # e.g., "open_refund_case"
        args = call["args"]        # e.g., {"user_id": "u123", ...}
        tool = self.tools[name]
        output = tool.invoke(args)  # Execute tool
        # Send result back to LLM for final summary
        tool_messages.append(ToolMessage(tool_call_id=call["id"], content=str(output)))
    
    # LLM makes final decision/summary
    final = self.llm.invoke([...messages..., ai, ...tool_messages...])
    reply_text = final.content
else:
    # No tools needed (e.g., policy explanation)
    reply_text = ai.content
```

**Output:**
```python
{
    "reply": "Case R10001 opened. We'll review within 5 business days...",
    "used_tools": [
        {"name": "open_refund_case", "args": {...}, "output": {...}}
    ],
    "updates": {
        "billing_case_id": "R10001",
        "context_flags": {"refund_in_progress": True}
    }
}
```

**State updates**: BillingAgent can update `context_flags` (e.g., `refund_in_progress: True`) to bias future routing decisions.

### 4. Fallback Agent (Clarification & Routing Hint)

**File**: `agents/fallback_agent.py`

**Purpose**: Handle unknown/ambiguous queries; ask for clarification; optionally hint at next route.

**Template response**:
```
I'm a specialist in technical support and billing.
I can help with service setup, technical issues, or payments/invoices.

Please clarify what you need (choose one option or add your own):
• [TECH] Internet drops / no internet / APN / Wi-Fi / bridge on ONT
• [BILLING] Plan & price / invoice / refund / case status
• [OTHER] Describe briefly — I'll route you to the right team.
```

**Route hint inference** (`_infer_route_hint`):
```python
tech_kw = ["wifi", "wi-fi", "apn", "pon", "router", "bridge", "internet", "5g", ...]
bill_kw = ["invoice", "faktura", "refund", "zwrot", "plan", "cena", ...]

if any(k in text.lower() for k in tech_kw):
    return "technical"
if any(k in text.lower() for k in bill_kw):
    return "billing"
return None
```

**Key insight**: FallbackAgent's hint is **advisory only**. The Router re-evaluates on next turn, allowing mid-conversation pivots.

**Return value:**
```python
{
    "reply": "I'm a specialist in technical support...",
    "route_hint": "technical" | "billing" | None
}
```

---

## Conversation State & Memory Management

### Multi-Turn Conversation Flow

**Scenario: 3-turn conversation**

```
Turn 1 (User query):
  Input:  session_id="s123", message="Internet is down"
  State:  history=[], last_agent=None
  → Router classifies as "technical"
  → TechnicalAgent retrieves docs, responds
  → State: history=[{role: "user", content: "Internet is down"}, 
                   {role: "assistant", content: "Based on docs..."}]
            last_agent="technical"

Turn 2 (User follow-up):
  Input:  session_id="s123", message="PON LED is blinking"
  State:  history=[...from Turn 1...]
  → Router sees recent "technical" context, classify as "technical" (high confidence)
  → TechnicalAgent responds (stays in same thread)
  → State: history=[...Turn 1..., {role: "user", content: "PON LED..."}, ...]
            last_agent="technical"

Turn 3 (Pivot to billing):
  Input:  session_id="s123", message="How much is the refund?"
  State:  history=[...from Turn 2...]
  → Router classifies as "billing" (high confidence, even though last_agent="technical")
  → Switches to BillingAgent
  → BillingAgent has access to full conversation history for context
  → State: last_agent="billing"
```

### State Persistence (FastAPI Sessions)

**File**: `main.py` — `AppState.sessions`

```python
class AppState:
    sessions: Dict[str, Dict[str, Any]] = {}

# In FastAPI endpoint:
@app.post("/chat")
async def chat(request: ChatRequest) -> ChatResponse:
    session_id = request.session_id
    
    # Load or initialize session
    state = AppState.sessions.get(session_id, {
        "history": [],
        "user_id": request.user_id,
        "last_agent": None,
        "context_flags": {}
    })
    
    # Execute one turn
    new_state = run_turn(AppState.graph, state, request.message)
    
    # Save updated state
    AppState.sessions[session_id] = new_state
    
    return ChatResponse(...)
```

**Key properties:**
- **Stateless graph**: Each `run_turn()` call receives complete state, returns new state
- **No side effects**: Graph doesn't mutate global state; only operates on passed-in `GraphState`
- **Easy persistence**: Can replace `AppState.sessions` dict with database (e.g., PostgreSQL, Redis)
- **Debuggable**: Full conversation history always available; no hidden context

### History Truncation (BillingAgent)

**Problem**: Conversation could grow indefinitely (>100K tokens).

**Solution** (BillingAgent):
```python
for m in state.history[-12:]:  # Last 12 messages (6 turns)
    # Rehydrate into LLM messages
```

**Reasoning:**
- Most relevant context is recent (last few turns)
- Older context often irrelevant for current billing decision
- Keeps token budget under control
- Sliding window of 6 conversation turns

**TechnicalAgent**: Uses entire history (typically shorter; RAG provides context).

---

## Hallucination Prevention & Safeguards

### 1. NO_CONTEXT Threshold (Primary Guard)

**Location**: `retriever/retriever.py` — `KBRetriever.retrieve()`

**Mechanism:**
```python
no_context = (len(items) < min_hits) or (mean_score < threshold)

if no_context:
    return {
        "docs": [],
        "no_context": True,
        "applied_threshold": 0.5
    }
```

**Criteria:**
- Fewer than 3 relevant chunks retrieved, **OR**
- Average cosine similarity of retrieved chunks < 0.5

**Outcome:**
- TechnicalAgent detects `no_context: True`
- Does NOT attempt to answer using weak context
- Instead: Asks for clarification with specific guidance

**Example:**
```
User: "fix my network"
Retrieved: [chunk1 (score=0.31), chunk2 (score=0.28), chunk3 (score=0.22)]
Mean score: 0.27 < 0.5
→ no_context = True
→ Agent: "I couldn't find enough info. Please share: device model, 
  access type (FTTH/DSL/5G), and symptoms (e.g., PON LED color)."
```

### 2. Source Citation Enforcement

**Location**: `agents/technical_agent.py` — `_format_sources()` & response cleanup

**Guarantee:**
- Every claim must have a source
- If LLM omits "Sources:" section, append it automatically
- Format: `Title — Section — File (version)`

**Code:**
```python
if "Sources:" not in text:
    text = text.rstrip() + "\n\nSources:\n" + sources_block
```

**Audit trail**: All sources include:
- Document title
- Section path (hierarchical)
- File name
- Version
- Relevance score (cosine similarity)

### 3. Instruction-Based Guards (System Prompts)

**TechnicalAgent System Prompt:**
```
You are TechnicalAgent. Answer ONLY using the provided CONTEXT chunks.
If the context is insufficient or unrelated, say so and ask for clarification.

Rules:
- Never invent facts beyond the CONTEXT.
- Always include a 'Sources' section.
- If NO_CONTEXT: ask for 1–2 clarifying details and mention what's missing.
```

**BillingAgent System Prompt:**
```
...
Rules:
- Use tools when needed. Ask for missing fields...
- Currency is PLN. Do NOT invent data.
- If request is outside billing scope, say so briefly.
```

**Key phrase: "Do NOT invent facts"** — Emphasizes that speculation is forbidden.

### 4. Semantic Routing Prevents Off-Topic Detours

**Router classifications:**
- Clear technical → TechnicalAgent (retrieves from KB)
- Clear billing → BillingAgent (calls tools)
- Unknown → FallbackAgent (asks for clarification)

**Prevents:** Accidental off-topic LLM behavior (e.g., general knowledge Q&A instead of support)

### 5. Tool-Calling Ensures Verifiable Answers (Billing)

**BillingAgent uses StructuredTool:**
```python
StructuredTool.from_function(
    name="get_subscription",
    description="Return subscription details for given user_id",
    func=get_subscription,
    args_schema=SubscriptionIn,  # Pydantic validation
    return_direct=False
)
```

**Guarantees:**
- LLM cannot invent subscription prices; must call tool
- Invalid arguments rejected by Pydantic schema
- All tool invocations logged and auditable
- Deterministic: same input → same output

### 6. Input Validation (Pydantic)

**BillingAgent input schemas:**
```python
class RefundCaseIn(BaseModel):
    user_id: str = Field(..., min_length=2, max_length=64)
    reason: RefundReason  # Enum: enforces valid values only
    amount_pln: PositiveFloat = Field(..., gt=0, le=1000.0)
    invoice_id: str = Field(..., min_length=3, max_length=64)
```

**Prevents:** Malformed tool calls, out-of-range amounts, typos in enum values.

---

## Complete Request Flow

### End-to-End Example: Technical Query

**User request:**
```json
{
  "session_id": "session_abc123",
  "message": "My router PON LED is blinking red. What's wrong?"
}
```

### Step-by-Step Execution:

**1. FastAPI endpoint receives request** (`main.py` — `/chat`)
```python
@app.post("/chat")
async def chat(request: ChatRequest) -> ChatResponse:
```

**2. Load or initialize session**
```python
state = AppState.sessions.get(session_id, {
    "history": [],
    "user_id": None,
    "last_agent": None,
    "context_flags": {}
})
```

**3. Append user message to history**
```python
state["history"].append({"role": "user", "content": "My router PON LED is blinking red..."})
```

**4. Execute graph via `run_turn()`** (`graph.py`)
```python
new_state = app.invoke(state)
```

**5. Router node processes** (`agents/router_agent.py`)
```
Message: "My router PON LED is blinking red..."
→ LLM (with system prompt)
→ Response: {"category": "technical", "confidence": 0.95, "reasoning": "..."}
→ state["route"] = "technical"
```

**6. Routing conditional edge** (`graph.py`)
```python
if route == "technical":
    route_to("technical")
```

**7. Technical node executes** (`agents/technical_agent.py`)

**7a. Retrieve documents**
```python
ret = self.retriever.retrieve("My router PON LED is blinking red...")
```

**7a.1 Embedding** (OpenAI text-embedding-3-small)
```
Query → 1536-dim vector
```

**7a.2 MMR search** (FAISS)
```
MMR(query, k=24, lambda=0.7)
→ [doc1, doc2, ..., doc24]
```

**7a.3 Dedup & rerank**
```
Remove redundant sections, apply boosts
→ [doc1_best, doc3_best, doc5_best, ..., doc8_best]
```

**7a.4 Score evaluation**
```
Mean score: 0.78
Hits: 8
→ no_context = False (0.78 > 0.5 threshold, 8 >= 3 min)
```

**7b. Build LLM context**
```
CONTEXT:
[SOURCE] Router LED Indicators — Troubleshooting — 02_router_wifi.md (v2.1)
PON LED (green/red/blinking):
- Green: Active connection, healthy
- Red: No signal detected
- Blinking: Synchronizing with ONT
...

QUESTION:
My router PON LED is blinking red. What's wrong?
```

**7c. LLM inference**
```
messages = [
    SystemMessage("You are TechnicalAgent..."),
    HumanMessage("CONTEXT:\n...\nQUESTION:\n...")
]
response = llm.invoke(messages)
```

**7d. LLM response:**
```
"The PON LED blinking indicates your router is synchronizing with the ONT (optical network terminal).
This is normal for the first 30 seconds after power-on. If it continues blinking for >2 minutes:

Steps:
1) Verify the fiber cable is firmly connected to the PON port
2) Check that the power adapter is providing 12V (green light on adapter)
3) Restart the router (power off 30s, power on)

Sources:
- Router LED Indicators — Troubleshooting — 02_router_wifi.md (v2.1)
- Router Setup — Power and Connections — 02_router_wifi.md (v2.0)"
```

**7e. Append to history**
```python
state["history"].append({
    "role": "assistant", 
    "content": "The PON LED blinking..."
})
state["last_agent"] = "technical"
state["last_docs"] = [
    {"title": "Router LED Indicators", "section": "Troubleshooting", ...},
    ...
]
```

**8. Graph execution ends** (`END` node)

**9. Save state**
```python
AppState.sessions[session_id] = new_state
```

**10. Format FastAPI response** (`main.py`)
```python
return ChatResponse(
    reply="The PON LED blinking...",
    route="technical",
    last_agent="technical",
    sources=[
        {"title": "Router LED Indicators", "section": "Troubleshooting", 
         "file": "02_router_wifi.md", "version": "2.1", "score": 0.82},
        ...
    ],
    used_tools=None,
    state_excerpt={"last_agent": "technical", "history_length": 2}
)
```

**11. HTTP response to client**
```json
{
  "reply": "The PON LED blinking indicates...",
  "route": "technical",
  "last_agent": "technical",
  "sources": [
    {"title": "Router LED Indicators", ..., "score": 0.82},
    {"title": "Power and Connections", ..., "score": 0.71}
  ],
  "used_tools": null,
  "state_excerpt": {"last_agent": "technical", "history_length": 2}
}
```

---

### End-to-End Example: Billing Query with Tool Calling

**User request (Turn 2 after pivot):**
```json
{
  "session_id": "session_xyz789",
  "user_id": "u123",
  "message": "I want to request a refund for invoice INV-20251001"
}
```

### Execution Flow:

**1-4: Same as above** (load state, append user message)

**5. Router node**
```
Message: "I want to request a refund for invoice INV-20251001"
→ Classification: {"category": "billing", "confidence": 0.98, ...}
→ state["route"] = "billing"
```

**6. Route to billing node**

**7. Billing node executes** (`agents/billing_agent.py`)

**7a. Prepare LLM messages**
```python
messages = [
    SystemMessage("You are BillingAgent..."),
    HumanMessage("[user_id=u123] I want to request a refund for invoice INV-20251001")
]
```

**7b. First LLM invocation** (with tools bound)
```
LLM sees: system prompt + user message + available tools
LLM decides: Need more info (reason, amount)
LLM response: "I can help with your refund. To proceed, I need:
1. Refund reason (overcharge, service outage, etc.)
2. Refund amount (in PLN)
Could you provide these details?"

ai.tool_calls = None  # No tools called yet
```

**7c. Extract and return**
```python
reply_text = "I can help with your refund..."
used_tools = []
updates = {}
```

**7d. Append to history**
```python
state["history"].append({"role": "assistant", "content": "I can help..."})
state["last_agent"] = "billing"
```

**8-11: Save and return to client**

---

### Turn 3: User provides details

**User request:**
```json
{
  "session_id": "session_xyz789",
  "user_id": "u123",
  "message": "Reason: overcharge. Amount: PLN 100"
}
```

**Execution:**

**7a. Prepare LLM messages** (with history)
```python
messages = [
    SystemMessage("You are BillingAgent..."),
    HumanMessage("[user_id=u123] I want to request a refund..."),  # Previous turn
    AIMessage("I can help with your refund..."),                   # Previous response
    HumanMessage("[user_id=u123] Reason: overcharge. Amount: PLN 100")  # Current
]
```

**7b. LLM invocation** (tools bound)
```
LLM now has context and user details
LLM decides: Call open_refund_case with extracted info

ai.tool_calls = [
    {
        "id": "call_123",
        "name": "open_refund_case",
        "args": {
            "user_id": "u123",
            "reason": "overcharge",
            "amount_pln": 100.0,
            "invoice_id": "INV-20251001",
            "description": None
        }
    }
]
```

**7c. Tool execution**
```python
for call in ai.tool_calls:
    tool = self.tools["open_refund_case"]
    output = tool.invoke(call["args"])
    # → Returns:
    # RefundCaseOut(
    #   case_id="R10001",
    #   status="opened",
    #   next_steps=["Case created for invoice INV-20251001.", ...],
    #   sla_business_days=5,
    #   eta_date=date(2025, 11, 6)
    # )
```

**7d. Feed tool result back to LLM**
```python
tool_messages = [
    ToolMessage(
        tool_call_id="call_123",
        content="RefundCaseOut(case_id='R10001', status='opened', ...)"
    )
]

final = self.llm.invoke([
    SystemMessage(...),
    HumanMessage(...),
    AIMessage(...),
    HumanMessage(...),
    ai,  # Original LLM response with tool_calls
    *tool_messages  # Tool results
])
```

**7e. LLM final summary**
```
"Your refund case R10001 has been opened. We've classified it as an overcharge.
A billing specialist will validate your charge within 5 business days.
If approved, PLN 100 will be refunded to your original payment method within 7-10 days.

Is there anything else I can help with?"
```

**7f. Extract updates**
```python
used_tools = [
    {"name": "open_refund_case", "args": {...}, "output": {...}}
]
updates = {
    "billing_case_id": "R10001",
    "context_flags": {"refund_in_progress": True}
}
```

**7g. Append to history**
```python
state["history"].append({"role": "assistant", "content": "Your refund case R10001..."})
state["last_agent"] = "billing"
state["context_flags"]["refund_in_progress"] = True
```

**8-11: Save and return**

```json
{
  "reply": "Your refund case R10001 has been opened...",
  "route": "billing",
  "last_agent": "billing",
  "used_tools": ["open_refund_case"],
  "state_excerpt": {
    "last_agent": "billing",
    "history_length": 6,
    "refund_in_progress": true,
    "billing_case_id": "R10001"
  }
}
```

---

## Key Design Principles

### 1. Explicit State Over Hidden Context

**Problem**: LLM agents often hide state in embeddings, gradients, or context managers.

**Solution**: All state is explicit in `GraphState` (TypedDict).
```python
class GraphState(TypedDict, total=False):
    history: List[Dict[str, str]]  # ← All conversation here
    last_agent: Optional[str]      # ← Current agent context
    context_flags: Dict[str, Any]  # ← Transient flags
    # ...no hidden state in LLM or retriever
```

**Benefits:**
- ✅ Debuggable (print state at any point)
- ✅ Testable (deterministic inputs → outputs)
- ✅ Persistent (easy to serialize, store in DB)
- ✅ Auditable (full conversation history)

### 2. Semantic Routing Over Keyword Matching

**Router uses LLM-based intent classification**, not simple regex:
```python
# ✗ Bad: keyword = "internet" in text.lower()
# ✓ Good: LLM classifies "moja sieć słaba" as "technical"
```

**Handles:** Synonyms, colloquialisms, Polish/English mix, context-dependent ambiguity.

### 3. RAG for Grounding, Tools for Verification

**Technical queries**: Use RAG (retrieval-augmented generation) with NO_CONTEXT threshold
- Prevents hallucination: "If docs don't cover it, say so"
- Sources mandatory: Cite every claim

**Billing queries**: Use tools (function calls) for deterministic actions
- No hallucination possible: Tool returns exact data or error
- Auditable: Every tool call logged with inputs/outputs

### 4. Graceful Degradation in Ambiguity

**Router strategy:**
- High confidence (>70%) & clear intent → Route to specialist
- Low confidence (<50%) → Route to FallbackAgent
- Mid-stream ambiguity with recent context → Stay with current agent (avoid jarring switches)

**Technical agent strategy:**
- Good retrieval results (score >0.5, >3 chunks) → Answer with sources
- Poor results → Ask for clarification, don't hallucinate

### 5. Multi-Turn Awareness

**Routing decision considers history:**
```python
if state.last_agent in ["technical", "billing"] and has_recent_context:
    # Low-confidence follow-up → stay with current agent
    if confidence < 0.7:
        route = state.last_agent
```

**Prevents:** Jarring agent switches mid-conversation.

### 6. Bounded Token Usage

**BillingAgent history truncation:**
- Keep last 12 messages (6 turns)
- Discards old context beyond sliding window

**TechnicalAgent context truncation:**
- Max 8KB of document context per query
- Sources ranked by relevance (MMR)

**Prevents:** Token overflow on long conversations; keeps latency acceptable.

### 7. Deterministic MVP for Production Readiness

**Mock data instead of external APIs:**
- `billing_tools.py` uses in-memory stores (`_USERS`, `_PLANS`)
- Deterministic, repeatable, offline-testable
- Easy to swap for real backend (PostgreSQL, REST APIs)

**No external dependencies beyond OpenAI:**
- FAISS is local (not external vector DB)
- LangGraph is local state machine (not external orchestrator)
- FastAPI is local (self-contained)

**Benefits:**
- ✅ No network latency variability
- ✅ Reproducible results (same query → same response)
- ✅ Cost-predictable (OpenAI calls only for LLM + embeddings)

---

## Summary: How It All Fits Together

```
┌─────────────────────────────────────────────────────────────┐
│                     USER REQUEST                            │
│                   (FastAPI /chat)                           │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
        ┌──────────────────────────────┐
        │  LOAD/INIT SESSION STATE     │
        │  (history, last_agent, ...)  │
        └──────────────┬───────────────┘
                       │
                       ▼
        ┌──────────────────────────────────────┐
        │  ROUTER NODE (LLM Classification)   │
        │  → "technical" | "billing" | ...    │
        └──────────────┬──────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
   ┌─────────┐  ┌──────────┐  ┌──────────────┐
   │ TECH    │  │ BILLING  │  │  FALLBACK    │
   │         │  │          │  │              │
   │ RAG:    │  │ TOOLS:   │  │ CLARIFY:     │
   │ • Retr. │  │ • Calls  │  │ • Ask for    │
   │ • LLM   │  │ • Tool   │  │   details    │
   │ • Cite  │  │ • LLM    │  │              │
   └────┬────┘  └────┬─────┘  └────┬─────────┘
        │            │             │
        └────────────┼─────────────┘
                     │
                     ▼
        ┌──────────────────────────────┐
        │  UPDATE STATE                │
        │  (history, last_agent, ...)  │
        └──────────────┬───────────────┘
                       │
                       ▼
        ┌──────────────────────────────┐
        │  SAVE SESSION STATE          │
        │  (AppState.sessions)         │
        └──────────────┬───────────────┘
                       │
                       ▼
        ┌──────────────────────────────┐
        │  RETURN ChatResponse         │
        │  (reply, sources, tools, ...) │
        └──────────────────────────────┘
```

**Key takeaways:**
- ✅ Every turn is **stateless** (graph receives explicit state, returns new state)
- ✅ No hidden LLM context (all in `history`)
- ✅ Hallucination prevention at every layer (NO_CONTEXT, citations, tools)
- ✅ Audit trail (sources, tool calls, routing decisions all logged)
- ✅ Production-ready (FastAPI, Pydantic validation, error handling)

---

## Appendix: Frequently Asked Questions

### Q: Why not just use a single LLM with context?

**A:** Single LLMs often:
- Hallucinate when docs don't cover a topic
- Treat technical and billing equally (lose focus)
- Can't reliably call tools without explicit orchestration
- Make non-deterministic routing decisions

**Multi-agent approach:**
- ✅ Each specialist is focused (better accuracy)
- ✅ RAG bounds technical agent to docs
- ✅ Tool-calling makes billing deterministic
- ✅ Router ensures optimal agent selection

### Q: What if the user switches topics abruptly?

**A:** Router re-evaluates **every turn**.
```
Turn 1: "Internet is down" → Router: technical (confidence 0.95) → TechnicalAgent
Turn 2: "How much do I owe?" → Router: billing (confidence 0.92) 
        → Switch to BillingAgent (high confidence overrides recent context)
```

The `_has_recent_agent_context` check only **biases** low-confidence decisions, not overrides high-confidence ones.

### Q: How do you prevent the billing agent from inventing prices?

**A:** Three layers:
1. **System prompt**: "Do NOT invent data"
2. **Tool binding**: LLM can only call `get_subscription(user_id)` to fetch real prices
3. **Pydantic validation**: Invalid tool arguments rejected before execution

Result: LLM cannot invent—it must call the tool.

### Q: What if the knowledge base is empty?

**A:** `NO_CONTEXT = True` → TechnicalAgent:
```
"I couldn't find enough information in the knowledge base.
Please share: device model, access type, and symptoms."
```

No hallucination, no fake docs, just honest "I don't know."

### Q: Can I add new tools to the BillingAgent?

**A:** Yes! `billing_tools.py` wraps functions as `StructuredTool`:
```python
StructuredTool.from_function(
    name="get_invoice_details",
    description="Fetch details for a given invoice_id",
    func=get_invoice_details,
    args_schema=InvoiceQueryIn,
    return_direct=False
)
```

Add to `as_langchain_tools()` list → automatically available to BillingAgent.

### Q: How do I integrate with a real database?

**A:** Replace mock functions in `billing_tools.py`:
```python
def get_subscription(user_id: str) -> SubscriptionOut:
    # ✗ Old: return _USERS.get(user_id)
    # ✓ New: SELECT * FROM subscriptions WHERE user_id = ?
    db = get_db_connection()
    sub = db.query(Subscription).filter_by(user_id=user_id).first()
    return SubscriptionOut(...)
```

Graph and LLM logic remain unchanged.

### Q: How do I audit all agent decisions?

**A:** Everything is in `GraphState`:
```python
state = {
    "history": [...],           # Full conversation
    "last_agent": "technical",  # Last router decision
    "last_docs": [...],         # Last sources used
    "_router_debug": [...]      # Router confidence + reasoning
}
```

Save `state` to database after each turn → full audit trail.

---

**End of Architecture Document**
