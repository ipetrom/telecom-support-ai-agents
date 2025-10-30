# Telecom Support AI Agents - Architecture Graph

## System Overview

This document showcases the **actual implemented architecture** of the Telecom Support AI Agents system, built with LangGraph, LangChain, and OpenAI.

---

## High-Level Architecture Flow

```
┌──────────────────────────────────────────────────────────────────────────┐
│                           FASTAPI APPLICATION                           │
│                              (main.py)                                   │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                    INITIALIZATION LAYER                           │ │
│  │                                                                    │ │
│  │  • OpenAI LLM (ChatOpenAI) → gpt-4o-mini                         │ │
│  │  • FAISS Retriever (KBRetriever) → data/docs                    │ │
│  │  • Billing Tools (as_langchain_tools)                           │ │
│  │  • BillingAgent with bound tools                                 │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                     ▼                                    │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                 LANGGRAPH STATE MACHINE                           │ │
│  │                      (graph.py)                                   │ │
│  │                                                                    │ │
│  │              GraphState (TypedDict)                              │ │
│  │              ─────────────────────                               │ │
│  │              • history: List[Dict]                               │ │
│  │              • user_id: Optional[str]                            │ │
│  │              • last_agent: Optional[str]                         │ │
│  │              • context_flags: Dict                               │ │
│  │              • last_docs: List (audit trail)                     │ │
│  │              • route: str (router decision)                      │ │
│  │              • reply: str (agent response)                       │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## LangGraph Execution Flow

```
                         ┌─────────────────┐
                         │     START       │
                         └────────┬────────┘
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │   ROUTER NODE           │
                    │  (RouterAgent)          │
                    │                         │
                    │  Input: Last user msg   │
                    │  Process:               │
                    │  • LLM classification   │
                    │  • Semantic analysis    │
                    │  • Confidence scoring   │
                    │  Output: route + debug  │
                    └──────────┬──────────────┘
                               │
                ┌──────────────┼──────────────┐
                │              │              │
    confidence>=0.7?  confidence>=0.7?  else
    category=         category=
    "technical"       "billing"
       │                 │            │
       ▼                 ▼            ▼
  ┌─────────────┐  ┌─────────────┐ ┌──────────────┐
  │ TECHNICAL   │  │  BILLING    │ │  FALLBACK    │
  │   NODE      │  │   NODE      │ │   NODE       │
  └─────────────┘  └─────────────┘ └──────────────┘
       │                 │            │
       └─────────────────┼────────────┘
                         │
                         ▼
                    ┌─────────────┐
                    │     END     │
                    └─────────────┘
```

---

## Detailed Agent Architecture

### 1. Router Agent (RouterAgent)
**Purpose**: Initial classification and routing decision

```
┌──────────────────────────────────────────────────────┐
│              ROUTER AGENT                            │
│         (agents/router_agent.py)                     │
└──────────────────────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
   ┌──────────┐   ┌──────────┐   ┌──────────────┐
   │ Semantic │   │ Multi-   │   │ Confidence   │
   │ Analysis │   │ lingual  │   │ Scoring      │
   │ via LLM  │   │ Support  │   │ (0.0 - 1.0)  │
   └──────────┘   └──────────┘   └──────────────┘
         │               │               │
         └───────────────┼───────────────┘
                         │
                    ┌────▼────┐
                    │ Decision│
                    │ Logic   │
                    └────┬────┘
                         │
     ┌───────────────────┼───────────────────┐
     │                   │                   │
   IF conf >= 0.7    IF conf >= 0.7    ELSE
   type="tech"       type="billing"    unknown
     │                   │                   │
  route:tech         route:billing      route:fallback
```

**Methods**:
- `route(state, user_msg)` → Returns `{"route": str, "confidence": float, "reasoning": str}`
- `_classify_intent()` → LLM invocation with error handling

---

### 2. Technical Agent (TechnicalAgent)
**Purpose**: Knowledge-based troubleshooting with RAG

```
┌──────────────────────────────────────────────────────┐
│           TECHNICAL AGENT                            │
│      (agents/technical_agent.py)                     │
└──────────────────────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
   ┌──────────┐   ┌──────────────┐ ┌──────────┐
   │  RAG     │   │   LLM        │ │  Source  │
   │Retriever │   │ Generation   │ │ Citation │
   │(FAISS)   │   │              │ │          │
   └──────────┘   └──────────────┘ └──────────┘
         │               │               │
         │ Documents     │ Answer        │ Sources
         │ from KB       │ + reasoning   │ metadata
         └───────────────┼───────────────┘
                         │
                    ┌────▼────────┐
                    │  Reply      │
                    │  + Sources  │
                    │  + last_docs│
                    └─────────────┘
```

**Components**:
- `KBRetriever` (retriever/retriever.py) - FAISS-based vector search
- RAG Chain: Retrieve → Generate → Cite

**Methods**:
- `run(state, user_msg)` → Returns `{"reply": str, "sources": List[Dict]}`

**Data Source**:
```
data/docs/
  ├── 01_troubleshooting_internet.md
  ├── 02_router_wifi.md
  ├── 03_apn_bridge.md
  └── 04_known_issues.md

artifacts/
  ├── index.faiss              (embeddings)
  ├── index_meta.json          (metadata)
  ├── embedder_info.json       (embedder config)
  └── stats.json               (index stats)
```

---

### 3. Billing Agent (BillingAgent)
**Purpose**: Transaction-safe operations with tool calling

```
┌──────────────────────────────────────────────────────┐
│            BILLING AGENT                             │
│       (agents/billing_agent.py)                      │
└──────────────────────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
   ┌──────────┐   ┌──────────────┐ ┌──────────┐
   │  Tool    │   │  LLM with    │ │ Context  │
   │ Calling  │   │  bind_tools()│ │ Flags    │
   │ LangChain│   │              │ │ for      │
   │ Tools    │   │              │ │ auditing │
   └──────────┘   └──────────────┘ └──────────┘
         │               │               │
    ┌────┴───────────────┼───────────────┘
    │                    │
    ▼                    ▼
  ┌─────────────────────────────────┐
  │  tools/billing_tools.py         │
  │                                 │
  │  • check_account()              │
  │  • get_billing_history()        │
  │  • create_support_case()        │
  │  • apply_refund()               │
  │  [all wrapped as LangChain]     │
  └─────────────────────────────────┘
         │
         ▼
    ┌────────────────┐
    │ Reply          │
    │ + Tool Results │
    │ + Updates      │
    └────────────────┘
```

**Methods**:
- `run(state, user_msg)` → Returns `{"reply": str, "updates": Dict}`

**Tool Integration**:
```python
from tools.billing_tools import as_langchain_tools
billing_tools = as_langchain_tools()
billing_agent = BillingAgent(llm=llm)
billing_agent.llm = llm.bind_tools(billing_tools)
```

---

### 4. Fallback Agent (FallbackAgent)
**Purpose**: Clarification and graceful degradation

```
┌──────────────────────────────────────────────────────┐
│           FALLBACK AGENT                             │
│      (agents/fallback_agent.py)                      │
└──────────────────────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
   ┌──────────┐   ┌──────────────┐ ┌──────────┐
   │Template- │   │No LLM        │ │ Multi-   │
   │Based     │   │(Deterministic)│ │lingual   │
   │Response  │   │Fast (<1ms)   │ │  UI      │
   └──────────┘   └──────────────┘ └──────────┘
         │               │               │
         └───────────────┼───────────────┘
                         │
            ┌────────────▼──────────────┐
            │ Clarification Prompt      │
            │ with Button/Menu Options  │
            │                           │
            │ • [TECH] Internet issues  │
            │ • [BILL] Invoices         │
            │ • [OTHER] Something else  │
            └───────────────────────────┘
```

**Methods**:
- `run(state, user_msg)` → Returns `{"reply": str}`

**Characteristics**:
- No LLM overhead
- Deterministic and fast
- Can preserve last_agent in state for context

---

## State Management & Data Flow

### GraphState Structure

```
GraphState (TypedDict)
│
├── history: List[Dict[str, str]]
│   └─ Conversation history
│      • {"role": "user", "content": "..."}
│      • {"role": "assistant", "content": "..."}
│
├── user_id: Optional[str]
│   └─ Customer identifier for billing context
│
├── last_agent: Optional[Literal["technical", "billing", "fallback"]]
│   └─ Previous agent for context preservation
│
├── context_flags: Dict[str, Any]
│   └─ Billing state, session data, flags
│
├── last_docs: List[Dict[str, Any]]
│   └─ Technical sources for audit trail
│      • {"title": "...", "excerpt": "...", "url": "..."}
│
├── route: Literal["technical", "billing", "fallback"]
│   └─ RouterAgent decision
│
├── reply: str
│   └─ Final agent response
│
└── _router_debug: List[Dict] (optional)
    └─ Router classification history
       • [{"route": "technical", "confidence": 0.95, "reasoning": "..."}]
```

### State Update Flow

```
                    ┌─────────────┐
                    │ User Input  │
                    └──────┬──────┘
                           │
                    ┌──────▼──────────────┐
                    │ run_turn()          │
                    │ Append to history   │
                    └──────┬──────────────┘
                           │
                    ┌──────▼──────────────┐
                    │ Graph Execution     │
                    │ (START → Router →   │
                    │  Agent → END)       │
                    └──────┬──────────────┘
                           │
      ┌────────────────────┼────────────────────┐
      │                    │                    │
      ▼                    ▼                    ▼
  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐
  │ Technical   │  │ Billing     │  │ Fallback     │
  │ updates:    │  │ updates:    │  │ updates:     │
  │ + history   │  │ + history   │  │ + history    │
  │ + last_docs │  │ + context_  │  │ + reply      │
  │ + reply     │  │   flags     │  │              │
  │ + last_agent│  │ + reply     │  │ + last_agent │
  │             │  │ + last_agent│  │              │
  └─────────────┘  └─────────────┘  └──────────────┘
      │                    │                    │
      └────────────────────┼────────────────────┘
                           │
                    ┌──────▼──────────────┐
                    │ Updated GraphState  │
                    │ Ready for next turn │
                    └─────────────────────┘
```

---

## Multi-Turn Conversation Loop

```
┌────────────────────────────────────────────────────────────────┐
│                  FastAPI Endpoint                             │
│              (POST /chat/conversation)                        │
└────────────────────────────────────────────────────────────────┘
                           │
                           ▼
            ┌──────────────────────────────┐
            │ Load Session from Store      │
            │ state = {                    │
            │   "history": [...],          │
            │   "user_id": "user123",      │
            │   "last_agent": null,        │
            │   ...                        │
            │ }                            │
            └──────────┬───────────────────┘
                       │
        ┌──────────────▼───────────────────┐
        │ Multiple Turns (Loop)            │
        │                                  │
        │ For i in range(num_turns):       │
        │                                  │
        │   1. Parse user_message_i        │
        │   2. run_turn(app, state, msg)   │
        │      ├─ Append msg to history    │
        │      ├─ app.invoke(state)        │
        │      │  └─ Execute graph         │
        │      └─ Return new_state         │
        │   3. Extract reply               │
        │   4. Add to response batch       │
        │   5. state = new_state           │
        │                                  │
        └──────────────┬───────────────────┘
                       │
            ┌──────────▼───────────────┐
            │ Save Updated Session     │
            │ (history, flags, etc.)   │
            └──────────┬───────────────┘
                       │
                       ▼
            ┌──────────────────────────┐
            │ Return Responses + State │
            │ to Client                │
            └──────────────────────────┘
```

---

## Component Interaction Diagram

```
                         ┌─────────────────────────┐
                         │   OpenAI API            │
                         │  (gpt-4o-mini)          │
                         └────────┬────────────────┘
                                  │
                                  │ invoke()
                                  │
        ┌─────────────────────────┴──────────────────────────┐
        │                                                    │
        ▼                                                    ▼
   ┌────────────┐                                   ┌─────────────┐
   │ RouterAgent│                                   │  Technical  │
   │   (llm)    │                                   │  Agent      │
   └────────────┘                                   │  (llm +     │
        │                                           │  retriever) │
        │ classification                            └─────────────┘
        │ + confidence                                   │
        │                                               │ query(
        │                                               │  vector)
        │                ┌──────────────────────────────┤
        │                │                              │
        │                │                              ▼
        │                │                        ┌──────────────┐
        │                │                        │   FAISS      │
        │                │                        │   Index      │
        │                │                        │  (artifacts/)│
        │                │                        └──────────────┘
        │                │
        ├────────────────┤ (conditional routing)
        │                │
        ▼                ▼
   ┌────────────┐   ┌──────────────┐
   │  Billing   │   │   Fallback   │
   │   Agent    │   │   Agent      │
   │  (llm +    │   │   (template) │
   │   tools)   │   └──────────────┘
   └────────────┘
        │
        │ bind_tools()
        ▼
   ┌────────────────┐
   │ Billing Tools  │
   │ (check_account,│
   │  get_history,  │
   │  create_case,  │
   │  apply_refund) │
   └────────────────┘
```

---

## Error Handling & Graceful Degradation

```
┌──────────────────────────────────────────────────────┐
│            Error Scenarios                           │
└──────────────────────────────────────────────────────┘
                     │
    ┌────────────────┼────────────────┐
    │                │                │
    ▼                ▼                ▼
┌─────────┐  ┌──────────────┐  ┌────────────┐
│ LLM API │  │  FAISS Query │  │  Tool Call │
│ Timeout │  │   Failure    │  │   Error    │
└────┬────┘  └──────┬───────┘  └─────┬──────┘
     │              │                │
     └──────────────┼────────────────┘
                    │
         ┌──────────▼──────────┐
         │ Catch Exception     │
         │ Log Error           │
         │ Return Fallback     │
         └──────────┬──────────┘
                    │
     ┌──────────────┼──────────────┐
     │              │              │
     ▼              ▼              ▼
┌─────────┐  ┌──────────┐  ┌────────────┐
│Router   │  │Technical │  │ Billing    │
│Returns: │  │Returns:  │  │ Returns:   │
│{        │  │{         │  │{           │
│ route:  │  │ reply:   │  │ reply:     │
│ error   │  │ "Sorry,  │  │ "I'm       │
│ conf:0  │  │ couldn't │  │ unable to  │
│}        │  │ find     │  │ process    │
│ →       │  │ docs"    │  │ this       │
│ fallback│  │}         │  │ request"   │
└─────────┘  └──────────┘  └────────────┘
     │              │              │
     └──────────────┼──────────────┘
                    │
            ┌───────▼────────┐
            │ User sees      │
            │ Fallback UI    │
            │ (clarification)│
            └────────────────┘
```

---

## Technology Stack

```
┌─────────────────────────────────────────────┐
│           TECHNOLOGY STACK                  │
├─────────────────────────────────────────────┤
│                                             │
│  Frontend → FastAPI                         │
│             ↓                               │
│  API Layer → Pydantic models                │
│             ↓                               │
│  Orchestration → LangGraph (StateGraph)     │
│                ↓                            │
│  Agents ─────→ LangChain (BaseChatModel)    │
│  │            ↓                             │
│  ├─ RouterAgent ───→ ChatOpenAI (LLM)      │
│  ├─ TechnicalAgent → ChatOpenAI + FAISS    │
│  ├─ BillingAgent ──→ ChatOpenAI + Tools    │
│  └─ FallbackAgent → Template-based          │
│                                             │
│  RAG Vector Store → FAISS                   │
│                   ├─ index.faiss            │
│                   ├─ embeddings             │
│                   └─ metadata               │
│                                             │
│  Knowledge Base → data/docs/ (Markdown)     │
│                                             │
│  Tools → LangChain tools wrapper            │
│        └─ billing_tools.py                  │
│                                             │
└─────────────────────────────────────────────┘
```

---

## Key Features

### 1. **Multi-Agent Specialization**
- Each agent has a specific role and expertise
- Router makes intelligent decisions
- Graceful fallback for ambiguous cases

### 2. **RAG Integration**
- FAISS vector database for fast retrieval
- Semantic document matching
- Source citation for transparency

### 3. **State Persistence**
- GraphState maintains conversation context
- Multi-turn support
- Audit trail for billing operations

### 4. **Multi-Lingual Support**
- LLM handles multiple languages naturally
- Templates localized where needed
- Fallback UI provides consistent experience

### 5. **Error Resilience**
- LLM errors → Fallback agent
- Tool failures → Graceful response
- Network issues → Deterministic fallback

### 6. **Transaction Safety**
- Billing agent with bound tools
- Context flags for auditing
- Idempotent operations where possible

---

## Execution Timeline Example

```
User: "Moja sieć nie działa"
│
├─ T=0ms:   run_turn() appends to history
├─ T=10ms:  app.invoke(state) starts
├─ T=20ms:  router_node() executes
│   ├─ Calls RouterAgent.route()
│   ├─ LLM.invoke() → "category: technical, confidence: 0.95"
│   └─ Sets state["route"] = "technical"
│
├─ T=300ms: _route_switch() evaluates "technical"
├─ T=310ms: technical_node() executes
│   ├─ Calls TechnicalAgent.run()
│   ├─ retriever.query_docs() → FAISS search
│   ├─ LLM.invoke() with context → Answer + sources
│   └─ state["reply"] = "Sprawdź routera..."
│
├─ T=600ms: app.invoke() completes → new_state
├─ T=610ms: FastAPI endpoint returns reply to user
│
Total latency: ~600ms (dominated by LLM calls)
```

---

## Summary

This architecture provides:

✅ **Intelligent Routing** - LLM-based semantic classification  
✅ **Specialized Agents** - Each handles its domain optimally  
✅ **Knowledge Integration** - RAG with FAISS for accurate information  
✅ **Multi-Turn Support** - State preserved across conversation  
✅ **Graceful Degradation** - Fallback for edge cases  
✅ **Production Ready** - Error handling and logging throughout  
✅ **Extensible** - Easy to add new agents or tools  

The system balances **intelligence** (LLM-based routing & responses) with **reliability** (deterministic fallback) and **performance** (FAISS for fast retrieval, template-based responses where appropriate).
