```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      TELECOM SUPPORT AI AGENTS                             │
│                                                                             │
│                  ROUTING ARCHITECTURE WITH LLM                             │
└─────────────────────────────────────────────────────────────────────────────┘


LEVEL 1: Input
═════════════════════════════════════════════════════════════════════════════
                              ┌──────────────────┐
                              │ User Message     │
                              │ e.g. "Moja sieć  │
                              │  nie działa"     │
                              └────────┬─────────┘
                                       │
                                       ▼

LEVEL 2: Initial Classification (NEW)
═════════════════════════════════════════════════════════════════════════════
                        ┌──────────────────────────┐
                        │    RouterAgent (LLM)     │
                        │   - Semantic Analysis    │
                        │   - Multi-lingual        │
                        │   - Confidence Score     │
                        │                          │
                        │  Input: "Moja sieć..."   │
                        │  ↓ (LLM invocation)      │
                        │  category: "technical"   │
                        │  confidence: 0.95        │
                        └────────────┬─────────────┘
                                     │
                ┌────────────────────┼────────────────────┐
                │                    │                    │
                ▼                    ▼                    ▼
        confidence >= 0.7 ?   confidence >= 0.7 ?  confidence >= 0.7 ?
        category="technical"  category="billing"   category="unknown" OR
                │                    │              confidence < 0.7
                ✅ YES               ✅ YES                  ❌ NO
                │                    │                      │

LEVEL 3: Specialist Routing
═════════════════════════════════════════════════════════════════════════════

  ┌─────────────────────────┐  ┌─────────────────────────┐  ┌─────────────────────┐
  │ TechnicalAgent          │  │ BillingAgent            │  │ FallbackAgent       │
  │                         │  │                         │  │                     │
  │ - RAG (retriever)       │  │ - Tool calling          │  │ - Ask for clarity   │
  │ - Cites sources         │  │ - Structured output     │  │ - No LLM            │
  │ - Knowledge-based       │  │ - Transaction-safe      │  │ - Template-based    │
  │                         │  │                         │  │                     │
  │ Input:                  │  │ Input:                  │  │ Input:              │
  │ "Moja sieć nie działa"  │  │ "Why charged twice?"    │  │ "Tell me a joke"    │
  │                         │  │                         │  │                     │
  │ Output:                 │  │ Output:                 │  │ Output:             │
  │ - Answer + Sources      │  │ - Tool result           │  │ - Clarification msg │
  │ - Troubleshooting steps │  │ - Case created          │  │ - "Pick option..."  │
  └─────────────────────────┘  └─────────────────────────┘  └─────────────────────┘


DECISION TREE
═════════════════════════════════════════════════════════════════════════════

User Message
    │
    ├─→ RouterAgent (LLM) invokes
    │   │
    │   ├─→ JSON Parse: category + confidence
    │   │
    │   └─→ Decision Logic:
    │       │
    │       ├─ IF confidence >= 0.7 AND category = "technical"
    │       │  THEN route = "technical"
    │       │       ├─→ [TechnicalAgent]
    │       │       ├─→ RAG search
    │       │       └─→ Answer with sources
    │       │
    │       ├─ IF confidence >= 0.7 AND category = "billing"
    │       │  THEN route = "billing"
    │       │       ├─→ [BillingAgent]
    │       │       ├─→ Tool calling
    │       │       └─→ Structured response
    │       │
    │       └─ ELSE (confidence < 0.7 OR category = "unknown")
    │          route = "fallback"
    │              ├─→ [FallbackAgent]
    │              ├─→ Ask for clarification
    │              └─→ No LLM (fast, deterministic)


EXAMPLES
═════════════════════════════════════════════════════════════════════════════

Example 1: Direct Technical
─────────────────────────────
Input:  "My internet is down"
Router: category="technical", confidence=0.98
Route:  "technical" → TechnicalAgent
Output: "Check your router... Sources: 01_troubleshooting.md"


Example 2: Polish Technical Synonym
────────────────────────────────────
Input:  "Moja sieć jest słaba"
Router: category="technical", confidence=0.92
Route:  "technical" → TechnicalAgent
Output: "[Answer in Polish with troubleshooting]"


Example 3: Billing with Variation
──────────────────────────────────
Input:  "Why was I charged twice?"
Router: category="billing", confidence=0.88
Route:  "billing" → BillingAgent
Output: "[Check account, create case if needed]"


Example 4: Ambiguous/Unknown
─────────────────────────────
Input:  "Tell me a joke"
Router: category="unknown", confidence=0.2
Route:  "fallback" → FallbackAgent
Output: "I'm a specialist in technical support and billing.
        Please clarify what you need:
        • [TECH] Internet issues, Wi-Fi, APN, connectivity
        • [BILLING] Invoices, refunds, plans, charges"


AGENT COMPARISON TABLE
═════════════════════════════════════════════════════════════════════════════

╔════════════════════════╦═══════════════════════╦═══════════════════════════╗
║ Aspect                 ║ RouterAgent           ║ FallbackAgent             ║
╠════════════════════════╬═══════════════════════╬═══════════════════════════╣
║ When invoked           ║ Every user message    ║ Only on route="fallback"  ║
║ Role                   ║ Initial classification║ Clarification + handoff   ║
║ LLM required?          ║ ✅ YES                ║ ❌ NO                     ║
║ Semantic?              ║ ✅ YES (LLM)          ║ ❌ NO (template)          ║
║ Language support       ║ ✅ Multi-lingual      ║ ✅ Multi-lingual          ║
║ Confidence score?      ║ ✅ YES (0.0-1.0)      ║ ❌ NO                     ║
║ Latency                ║ ~300-500ms (LLM)      ║ <1ms (deterministic)      ║
║ Accuracy               ║ 90-95% (semantic)     ║ 60-70% (keyword)          ║
║ Cost per call          ║ ~$0.0001              ║ $0                        ║
║ Failure mode           ║ Falls back to unknown │ Always succeeds           ║
╚════════════════════════╩═══════════════════════╩═══════════════════════════╝


FLOW WITH EDGE CASES
═════════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────┐
│ Scenario: LLM Unavailable (Network Error)                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  User → RouterAgent._classify_intent()                             │
│           ├─ LLM.invoke() ← ERROR (timeout)                        │
│           ├─ Catch JSONDecodeError / ConnectionError               │
│           └─ Return: {                                             │
│                "category": "unknown",                              │
│                "confidence": 0.0,                                  │
│                "reasoning": "Classification error: [...]"          │
│              }                                                     │
│           ↓                                                         │
│        route.route() → route = "fallback"                          │
│           ↓                                                         │
│        [FallbackAgent] ← Ask for clarification                     │
│                                                                     │
│  ✅ Graceful degradation: Falls back to manual classification     │
└─────────────────────────────────────────────────────────────────────┘


DATA FLOW: State Updates
═════════════════════════════════════════════════════════════════════════════

ConversationState:
┌──────────────────────────────────────┐
│ .history: List[Dict]                 │
│   ├─ {"role": "user", "content": ".."}
│   ├─ {"role": "assistant", "content": ".."}
│   └─ ...                              │
│ .last_agent: Optional[str]           │
│   ├─ "technical"                     │
│   ├─ "billing"                       │
│   └─ "fallback"                      │
└──────────────────────────────────────┘
       ↑                    ↑
       │                    │
    RouterAgent         FallbackAgent
    updates:            preserves:
    route value         history
    classification      last_agent


INTEGRATION CHECKLIST
═════════════════════════════════════════════════════════════════════════════

□ Initialize RouterAgent with LLM in graph.py
  router = RouterAgent(llm=ChatOpenAI(...))

□ Initialize FallbackAgent in graph.py
  fallback = FallbackAgent()

□ Create router_node that calls router.route()
  
□ Connect routing decisions to specialist agents
  
□ Update state transitions to track last_agent
  
□ Test with multiple scenarios (edge cases)
  
□ Monitor confidence scores in production
  
□ Add logging for misrouted cases


```
