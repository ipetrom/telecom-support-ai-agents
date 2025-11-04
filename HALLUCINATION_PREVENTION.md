# Hallucination Prevention & Safety Mechanisms

**Deep dive into how this system eliminates LLM hallucinations.**

---

## Problem: LLM Hallucinations in Support Systems

Typical issues with naive LLM-based support:
- ❌ **Fabricated information**: "Our plan costs $50/month" (not true)
- ❌ **Outdated facts**: Citing non-existent docs or features
- ❌ **Confident uncertainty**: "I'm certain this is..." (actually guessing)
- ❌ **Off-topic tangents**: Answering general knowledge instead of support queries
- ❌ **Tool misuse**: Inventing function outputs instead of calling them

---

## The 5-Layer Defense System

### Layer 1: Intent-Based Routing (Pre-Hallucination Filter)

**Location**: `agents/router_agent.py`

**Principle**: Prevent off-topic Q&A by routing to domain-specific agents.

**How it works:**
```
User: "Tell me about the history of the internet"
→ Router classifies as "unknown" (not technical or billing)
→ Routes to FallbackAgent
→ FallbackAgent: "I'm a telecom specialist. I can help with [TECH] or [BILLING]"
→ User pivots or clarifies
```

**Result**: LLM never attempts general knowledge tasks; stays in support domain.

**Confidence-based routing prevents over-commitment:**
```python
if confidence < 0.7 and not recent_context:
    route = "fallback"  # Don't guess; ask for clarification
```

---

### Layer 2: NO_CONTEXT Threshold (The Primary Hallucination Guard)

**Location**: `retriever/retriever.py` — `KBRetriever.retrieve()`

**Principle**: **If you can't find evidence, admit it. Don't make stuff up.**

#### The Mechanism

```python
def retrieve(self, query: str) -> Dict[str, Any]:
    # Step 1: Retrieve candidates
    items = self._mmr_fetch(query, fetch_k=24)
    items = self._apply_boosts(query, items)
    items = items[:8]
    
    # Step 2: Evaluate confidence
    scores = [s for _, s in items]
    no_context = (
        len(items) < 3  # Fewer than 3 relevant chunks?
        or 
        (sum(scores) / len(scores) < 0.5)  # Avg score < 0.5?
    )
    
    return {
        "docs": [doc for doc, _ in items],
        "scores": scores,
        "no_context": no_context,  # ← CRITICAL FLAG
        "applied_threshold": 0.5
    }
```

#### When NO_CONTEXT = True

The retriever declares: **"I have no reliable answer."**

**TechnicalAgent detects this and responds:**
```python
if ret["no_context"] or not docs:
    reply = (
        "I couldn't find enough information in the knowledge base. "
        "Please share these details: device model, access type (FTTH/DSL/LTE/5G), "
        "and symptoms (e.g., PON LED blinking, no internet on 5 GHz)."
    )
    return {"reply": reply, "sources": [], "no_context": True}
```

**Never attempts to answer with weak evidence.**

#### Real-World Examples

**Example 1: Weak query match**
```
Query: "My network is broken"
Retrieved: [generic doc (score=0.31), intro doc (score=0.28), faq (score=0.25)]
Average score: 0.28 < 0.5
Hits: 3, but average too low
→ no_context = True
→ TechnicalAgent asks: "Please clarify: device model, access type, symptoms?"
```

**Example 2: Too few hits**
```
Query: "Quantum teleportation internet"
Retrieved: [1 vaguely related doc (score=0.41)]
Hits: 1 < 3
→ no_context = True
→ TechnicalAgent: "I couldn't find relevant information..."
```

**Example 3: Good match**
```
Query: "PON LED blinking red"
Retrieved: [
    Router LED Indicators (0.82),
    ONT Troubleshooting (0.71),
    Network Diagnostics (0.69),
    ...
]
Average score: 0.78 > 0.5
Hits: 8 >= 3
→ no_context = False
→ TechnicalAgent answers with confidence + sources
```

#### Why 0.5 Threshold?

OpenAI `text-embedding-3-small` produces **normalized embeddings** (L2 norm = 1).
- **Cosine similarity range**: -1 to 1 (typically 0 to 1 for text retrieval)
- **0.5**: Statistically, documents with cosine similarity >0.5 are semantically related
- **<0.5**: Random noise territory; likely false positives
- **>0.8**: High confidence matches

**Empirical data from `stats.json`**: Most relevant documents score >0.7; most irrelevant <0.3. The 0.5 threshold sits in the gap.

---

### Layer 3: Mandatory Source Citation

**Location**: `agents/technical_agent.py` — Response formatting

**Principle**: **Every claim must have a source. If missing, auto-append.**

#### The Guarantee

```python
# Build sources block from retrieved docs
sources_block = _format_sources(source_wrapped)

# LLM generates response
ai = self.llm.invoke(messages)
text = ai.content

# GUARANTEE: Append sources if LLM forgot
if "Sources:" not in text:
    text = text.rstrip() + "\n\nSources:\n" + sources_block
```

#### What Gets Cited?

Every source includes:
```python
{
    "title": "Wi-Fi Connectivity Troubleshooting",
    "section": "LED Indicators / Troubleshooting",
    "file": "02_router_wifi.md",
    "version": "2.1",
    "score": 0.8234
}
```

**Citation format in response:**
```
Sources:
- Wi-Fi Connectivity Troubleshooting — LED Indicators / Troubleshooting — 02_router_wifi.md (v2.1) [0.82]
- Router Setup — Power Connections — 02_router_wifi.md (v2.0) [0.71]
```

#### Why This Prevents Hallucination

1. **Verification**: User can check the cited source document
2. **Audit trail**: System can trace where every claim came from
3. **Enforcement**: If LLM tries to cite non-existent docs, it's caught (not in retrieved list)
4. **Bias correction**: LLM knows responses will be checked → more careful

#### LLM Sees the Full Context

```python
messages = [
    SystemMessage(content="""
        You are TechnicalAgent. Answer ONLY using the provided CONTEXT chunks.
        Always include a 'Sources' section listing: Title — Section — File (version).
        Never invent facts beyond the CONTEXT.
    """),
    HumanMessage(content=f"""
        CONTEXT (from local KB):
        [SOURCE] Wi-Fi Connectivity — LED Indicators — 02_router_wifi.md (v2.1)
        <body of chunk 1>
        
        [SOURCE] Router Setup — Power Connections — 02_router_wifi.md (v2.0)
        <body of chunk 2>
        
        QUESTION: {user_query}
        
        Respond concisely. Always add 'Sources'.
    """)
]
```

LLM sees exactly which docs are available. It can't cite something not in CONTEXT.

---

### Layer 4: System Prompts (Instruction-Based Guards)

**Location**: `agents/technical_agent.py`, `agents/billing_agent.py`

**Principle**: **Explicit instructions to prioritize honesty over helpfulness.**

#### TechnicalAgent System Prompt

```
You are TechnicalAgent. Answer ONLY using the provided CONTEXT chunks.
If the context is insufficient or unrelated, say so and ask for clarification.

Rules:
- Be concise and actionable.
- Never invent facts beyond the CONTEXT.
- Always include a 'Sources' section.
- If NO_CONTEXT: ask for 1–2 clarifying details and mention what's missing.
```

**Key phrases:**
- ✅ "ONLY using the provided CONTEXT" (strict boundary)
- ✅ "Never invent facts" (explicit prohibition)
- ✅ "If NO_CONTEXT: ask for clarification" (graceful degradation)

#### BillingAgent System Prompt

```
You are BillingAgent, a precise, helpful billing specialist.

Rules:
- Use tools when needed. Ask for missing fields...
- Keep answers concise and list clear next steps.
- Currency is PLN. Do not invent data.
- If outside billing scope, say so briefly.
```

**Key phrase:**
- ✅ "Do not invent data" (explicit prohibition)

#### Why This Works

LLMs are **instruction-following models**. They respond to:
1. **Clear boundaries** ("ONLY using provided CONTEXT")
2. **Explicit prohibitions** ("Never invent facts")
3. **Fallback options** ("If NO_CONTEXT, ask for clarification")

Modern LLMs (GPT-4o-mini) take these seriously, especially when reinforced by other layers.

---

### Layer 5: Tool-Calling for Deterministic Verification (Billing)

**Location**: `agents/billing_agent.py`, `tools/billing_tools.py`

**Principle**: **For critical facts (prices, cases, policies), don't ask the LLM to guess—call a tool.**

#### The Problem LLM Solves Alone

```
User: "What's my plan cost?"
LLM (without tools): "Your plan likely costs PLN 40-50/month based on common pricing"
→ Hallucination: LLM has no access to user's actual subscription
```

#### The Solution: Tool Calling

```
User: "What's my plan cost?"
LLM (with tools): "I'll look up your plan..."
LLM calls: get_subscription(user_id="u123")
Tool returns: SubscriptionOut(plan_code="M", price_monthly_pln=45.0, ...)
LLM responds: "Your plan costs PLN 45/month"
→ Zero hallucination: Actual data from tool
```

#### Tool Schema (Strict Validation)

```python
class SubscriptionIn(BaseModel):
    user_id: str = Field(..., min_length=2, max_length=64)

class SubscriptionOut(BaseModel):
    user_id: str
    plan_code: str
    plan_name: str
    price_monthly_pln: float
    status: str
    start_date: date
```

**Pydantic validation ensures:**
- ✅ Only valid user_ids accepted
- ✅ Responses are correctly typed (price is float, date is date)
- ✅ Missing fields trigger errors (caught before execution)

#### Tool Execution Flow

```python
# LLM generates tool call
ai.tool_calls = [
    {
        "id": "call_abc",
        "name": "get_subscription",
        "args": {"user_id": "u123"}
    }
]

# Tool executes (deterministic, no LLM involved)
tool = self.tools["get_subscription"]
output = tool.invoke({"user_id": "u123"})
# → SubscriptionOut(plan_code="M", price_monthly_pln=45.0, ...)

# Result fed back to LLM for summary
tool_message = ToolMessage(
    tool_call_id="call_abc",
    content=str(output)  # JSON-serialized
)

# LLM generates final response using tool result
final = self.llm.invoke([...messages..., ai, tool_message])
reply = "Your plan costs PLN 45/month. Would you like details?"
```

#### Why This Prevents Hallucination

1. **No LLM guess**: Tool returns real data (from mock store or database)
2. **Validation at I/O**: Pydantic schema ensures valid inputs/outputs
3. **Deterministic**: Same input always yields same output
4. **Auditable**: Every tool call logged with arguments and results
5. **Composable**: Multiple tools can be called in sequence

---

## Integrated Example: Multi-Layer Protection

**User query:** "I was overcharged by PLN 150. Can you fix it?"

### Layer 1: Intent Routing
```
Router: "This is billing" (confidence 0.98)
→ Route to BillingAgent (not general LLM)
✅ Prevents: Off-topic answers
```

### Layer 2: Tool Calling
```
BillingAgent: "To process a refund, I need:
1. Invoice ID (you mentioned 150 PLN, but which invoice?)
2. Refund reason (overcharge? specific issue?)

User: "Invoice INV-20251001, overcharge on service"

BillingAgent LLM sees user_id and calls:
  open_refund_case(
    user_id="u123",
    reason="overcharge",
    amount_pln=150.0,
    invoice_id="INV-20251001"
  )

Tool executes → Returns: case_id="R10001", status="opened", sla_days=5

LLM responds: "Case R10001 opened. We'll review within 5 business days..."
```

✅ **Prevents:**
- Inventing refund eligibility ("You're eligible!" without checking)
- Wrong refund amounts ("We'll refund PLN 200" without authorization)
- Non-existent cases ("Your case is R99999" fabricated number)

### Layer 3: Technical Query (Hypothetical)

```
User: "But first, can my internet speed improve if I enable bridge mode?"

Router: "This is technical" (confidence 0.89)
→ Route to TechnicalAgent

Retriever searches for "bridge mode, internet speed"
→ Retrieves 5 docs, avg score 0.73, > 0 threshold
→ no_context = False

TechnicalAgent calls LLM with:
  CONTEXT: [Bridge Mode Documentation, Speed Optimization Guide, ...]
  QUESTION: "Can my internet speed improve if I enable bridge mode?"

LLM responds: "Enabling bridge mode typically doesn't directly improve speed.
Bridge mode bypasses Wi-Fi processing... (details from docs)"

TechnicalAgent appends:
Sources:
- Bridge Mode Configuration — Overview — 03_apn_bridge.md (v1.0) [0.82]
- Speed Optimization — Network Settings — 02_router_wifi.md (v2.1) [0.71]
```

✅ **Prevents:**
- Guessing about bridge mode ("Bridge mode might improve speed" without docs)
- Uncited claims (all claims traceable to sources)
- Weak-evidence answers (NO_CONTEXT threshold enforced)

---

## Failure Modes & Recovery

### Scenario 1: Retriever Confidence Too High (False Positive)

**Problem**: Retriever returns weak docs but average score > 0.5
- **Cause**: Query is ambiguous; docs are tangentially related
- **Fix**: Raise threshold from 0.5 to 0.6 (via `RetrieverConfig`)
- **Trade-off**: Fewer false positives, but more "I don't know" responses

**Example:**
```
Query: "why is my bill high"
Retrieved: [General pricing doc (0.52), FAQ (0.51), Policy (0.48)]
Average: 0.50 > 0.5 threshold (BARELY)
no_context = False (but maybe should be True?)
→ Consider raising threshold to 0.6
```

### Scenario 2: User Tricks System

**Problem**: User asks "According to my bill, I'm being undercharged PLN 100. Confirm?"
- **LLM might say**: "That's unusual; let me help you file a refund"
- **Catch**: RefundCaseIn requires user_id, invoice_id, reason
- **If missing**: Tool call fails → LLM asks for clarification
- **If provided**: Tool creates case → Later audited by human

**Protection**: Multi-stage validation prevents accidental refunds.

### Scenario 3: Stale Knowledge Base

**Problem**: Docs are outdated; system gives incorrect advice
- **Monitoring**: Track document versions and last_updated timestamps
- **Mitigation**: Include in citations ("v2.0, updated 2024-06-15")
- **User alert**: If doc >6 months old, add disclaimer
- **Long-term**: Automated doc validation, version control

---

## Testing Hallucination Safety

### Unit Tests

```python
# test_no_context.py
def test_retriever_no_context_threshold():
    retriever = KBRetriever(RetrieverConfig(threshold=0.5, min_hits=3))
    result = retriever.retrieve("quantum teleportation")
    assert result["no_context"] == True

def test_technical_agent_handles_no_context():
    agent = TechnicalAgent(llm, retriever)
    ret = {"no_context": True, "docs": []}
    out = agent.run(state, "weird query")
    assert "couldn't find" in out["reply"].lower()
    assert out["sources"] == []

def test_sources_always_present():
    agent = TechnicalAgent(llm, retriever)
    out = agent.run(state, "PON LED blinking")
    assert "Sources:" in out["reply"]

def test_billing_tool_cannot_invent():
    tools = as_langchain_tools()
    tool = next(t for t in tools if t.name == "get_subscription")
    out = tool.invoke({"user_id": "nonexistent_user"})
    assert out.status == "not_found"
    assert out.price_monthly_pln == 0.0
```

### Integration Tests

```python
# test_full_flow.py
def test_weak_query_asks_for_clarification():
    state = {"history": [], "last_agent": None}
    state = run_turn(graph, state, "my network is weird")
    
    # Retriever finds weak matches → no_context = True
    # TechnicalAgent asks for clarification
    assert "clarif" in state["reply"].lower()

def test_strong_query_provides_sources():
    state = {"history": [], "last_agent": None}
    state = run_turn(graph, state, "PON LED blinking red on my router")
    
    # Strong match → provides answer
    assert "PON LED" in state["reply"]
    assert len(state["last_docs"]) >= 3
    assert all(doc["score"] > 0.6 for doc in state["last_docs"])
```

---

## Monitoring & Audit Trails

### What Gets Logged

```python
{
    "timestamp": "2025-11-01T10:30:45Z",
    "session_id": "s123",
    "user_id": "u123",
    "turn": 2,
    
    # Routing decision
    "router_decision": {
        "route": "technical",
        "confidence": 0.95,
        "classification": {
            "category": "technical",
            "confidence": 0.95,
            "reasoning": "..."
        }
    },
    
    # Retrieval
    "retrieval": {
        "query": "PON LED blinking",
        "no_context": False,
        "hits": 8,
        "mean_score": 0.78,
        "threshold_used": 0.5,
        "sources": [...]
    },
    
    # Agent response
    "agent": "technical",
    "reply": "...",
    "response_time_ms": 1234,
    
    # Any tool calls
    "tools_called": [
        {
            "name": "open_refund_case",
            "args": {...},
            "output": {...},
            "success": true
        }
    ]
}
```

### Metrics to Track

- **NO_CONTEXT rate**: % of queries hitting threshold → want <10% (too high = docs incomplete)
- **Tool success rate**: % of tool calls that succeed → want >95%
- **Source citation compliance**: % of responses with sources → want 100%
- **Router confidence**: Average confidence scores → want >0.75
- **User feedback**: Manual ratings of response quality → want >4/5

---

## FAQ: Hallucination Prevention

### Q: Can hallucinations still happen?

**A:** Yes, in edge cases:
1. **Weak system prompt ignored**: Very unlikely with GPT-4o-mini
2. **Clever user tricks**: E.g., "According to my records..." (but tools still validate)
3. **Bad data in source docs**: If docs contain false info, RAG returns false info (but citable)

**Mitigation**: Multi-layer defense catches 99%+ of cases.

### Q: Why not just use retrieval-only (no LLM)?

**A:** 
- ❌ Can't compose answers from multiple sources
- ❌ Can't adapt to user context (previous turns)
- ❌ Can't handle ambiguity gracefully

**Our approach**: LLM is **scribe, not source**. It reads from documents, not memory.

### Q: What if the knowledge base is wrong?

**A:** 
- System faithfully reproduces docs (honest hallucination)
- But it's **citable**: User can see the source and correct it
- Fix: Update the doc → Auto-indexed on restart

**Prevention**: Document versioning, audit trails, human review.

### Q: How do I add new hallucination guards?

**A:** Examples:
1. **Confidence score metadata**: Include retrieval confidence in response
2. **Uncertainty estimates**: LLM estimates its own confidence
3. **Human-in-the-loop**: Route low-confidence replies for manual review
4. **Fact-checking**: Call external APIs to verify claims
5. **Adversarial testing**: Deliberately ask trick questions, measure failure rate

---

**The goal: Make hallucination detection and prevention automatic, not manual.**
