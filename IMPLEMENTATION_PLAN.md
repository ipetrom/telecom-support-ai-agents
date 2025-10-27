# 📋 Step-by-Step Implementation Plan

## Overview

This document provides a **complete implementation roadmap** from initial setup to production deployment, with concrete milestones, deliverables, and validation steps.

---

## 🎯 Phase 1: Foundation & Setup (Week 1)

### Milestone 1.1: Environment Setup
**Duration**: 1 day

**Tasks**:
1. ✅ Clone repository
2. ✅ Create virtual environment
3. ✅ Install dependencies
4. ✅ Configure `.env` with OpenAI API key

**Commands**:
```bash
git clone <repo>
cd telecom-support-ai-agents
./setup.sh
```

**Validation**:
```bash
python -c "from config import settings; print(settings.openai_model)"
# Should output: gpt-4o-mini
```

**Deliverables**:
- ✅ Working Python environment
- ✅ Configuration loaded
- ✅ No import errors

---

### Milestone 1.2: Vector Store Initialization
**Duration**: 0.5 days

**Tasks**:
1. ✅ Review technical documentation in `data/docs/`
2. ✅ Run vector store builder
3. ✅ Verify FAISS index created

**Commands**:
```bash
python retriever/build_vectorstore.py
```

**Validation**:
```bash
ls data/vectorstore/
# Should show: index.faiss, index.pkl
```

**Deliverables**:
- ✅ FAISS vector store persisted
- ✅ 4 documents embedded (auth_faq, integration_guide, rate_limits, troubleshooting)
- ✅ Retrieval test passes

**Optimization Notes**:
- 💡 For faster embedding: Use `text-embedding-3-small` (cheaper, slightly lower quality)
- 💡 For better retrieval: Increase `chunk_overlap` to 300 (more context)

---

### Milestone 1.3: Basic Testing
**Duration**: 0.5 days

**Tasks**:
1. ✅ Test router classification
2. ✅ Test retriever with sample query
3. ✅ Test billing tools (mock data)

**Commands**:
```bash
# Test retriever
python -c "
from retriever.retriever import get_retriever
retriever = get_retriever()
context = retriever.get_context_for_query('How do I authenticate?')
print(context[:200])
"

# Test tools
python -c "
from tools.billing_tools import get_subscription
result = get_subscription('user_12345')
print(result)
"
```

**Deliverables**:
- ✅ Router classifies 10 test messages correctly
- ✅ Retriever returns relevant context
- ✅ Tools execute without errors

---

## 🤖 Phase 2: Agent Implementation (Week 2)

### Milestone 2.1: Router Agent
**Duration**: 1 day

**Implementation Checklist**:
- ✅ `RouterAgent` class with OpenAI client
- ✅ System prompt loading from file
- ✅ JSON parsing with error handling
- ✅ State update logic

**Testing**:
```python
from router.router_agent import RouterAgent
from state import create_initial_state
from langchain_core.messages import HumanMessage

router = RouterAgent()

# Test technical classification
state = create_initial_state("user_1", HumanMessage(content="API is broken"))
state = router(state)
assert state["current_category"] == "technical"

# Test billing classification
state = create_initial_state("user_2", HumanMessage(content="I want a refund"))
state = router(state)
assert state["current_category"] == "billing"
```

**Deliverables**:
- ✅ 95%+ classification accuracy on test set
- ✅ Fallback to "other" on parse errors
- ✅ Logs show classification decisions

---

### Milestone 2.2: Technical Agent
**Duration**: 1.5 days

**Implementation Checklist**:
- ✅ `TechnicalAgent` class
- ✅ Integration with `TechnicalRetriever`
- ✅ Context injection into system prompt
- ✅ Source attribution in responses

**Testing**:
```python
from agents.technical_agent import TechnicalAgent

agent = TechnicalAgent()
state = create_initial_state("user_1", HumanMessage(content="How do I use OAuth?"))
state["current_category"] = "technical"
state = agent(state)

response = state["messages"][-1].content
assert "OAuth" in response or "authentication" in response.lower()
assert state["retrieved_context"] is not None
```

**Validation Criteria**:
- ✅ Answers reference source documents
- ✅ Refuses to answer if context insufficient
- ✅ No hallucinated information

**Anti-Hallucination Test**:
```python
# Ask about something NOT in docs
state = create_initial_state("user_1", HumanMessage(content="What's the weather?"))
state["current_category"] = "technical"
state = agent(state)
response = state["messages"][-1].content
assert "don't have information" in response.lower()
```

---

### Milestone 2.3: Billing Agent
**Duration**: 1.5 days

**Implementation Checklist**:
- ✅ `BillingAgent` class
- ✅ Tool binding with `@tool` decorator
- ✅ User ID injection from state
- ✅ Tool execution loop (max 5 iterations)

**Testing**:
```python
from agents.billing_agent import BillingAgent

agent = BillingAgent()

# Test subscription query
state = create_initial_state("user_12345", HumanMessage(content="What's my plan?"))
state["current_category"] = "billing"
state = agent(state)
response = state["messages"][-1].content
assert "Premium 5G" in response

# Test refund request
state = create_initial_state("user_12345", HumanMessage(content="I want a refund"))
state["current_category"] = "billing"
state = agent(state)
response = state["messages"][-1].content
assert "REF-" in response  # Case ID
```

**Tool Call Verification**:
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python main.py --cli
# Send: "What's my plan?"
# Logs should show: "Executing tool: get_subscription_tool"
```

---

### Milestone 2.4: Fallback Agent
**Duration**: 0.5 days

**Implementation Checklist**:
- ✅ `FallbackAgent` class (no LLM)
- ✅ Static clarification template
- ✅ Sets `needs_clarification` flag

**Testing**:
```python
from agents.fallback_agent import FallbackAgent

agent = FallbackAgent()
state = create_initial_state("user_1", HumanMessage(content="Hello"))
state["current_category"] = "other"
state = agent(state)

response = state["messages"][-1].content
assert "specialist in technical support and billing" in response.lower()
assert state["needs_clarification"] == True
```

---

## 🔗 Phase 3: Orchestration (Week 3)

### Milestone 3.1: LangGraph Construction
**Duration**: 2 days

**Implementation Checklist**:
- ✅ `create_support_graph()` function
- ✅ Add all 4 nodes (router, technical, billing, fallback)
- ✅ Conditional edge based on category
- ✅ Memory integration with `MemorySaver`

**Testing**:
```python
from graph import create_support_graph
from state import create_initial_state
from langchain_core.messages import HumanMessage

graph = create_support_graph()

# Test full flow
config = {"configurable": {"thread_id": "test-123"}}
state = create_initial_state("user_1", HumanMessage(content="API authentication help"))
result = graph.invoke(state, config)

assert result["last_agent"] in ["technical", "billing", "fallback"]
assert len(result["messages"]) >= 2  # User + AI response
```

**Graph Visualization**:
```python
from graph import visualize_graph
diagram = visualize_graph(graph)
print(diagram)  # Should show Mermaid diagram
```

---

### Milestone 3.2: Multi-Turn Conversations
**Duration**: 1 day

**Testing**:
```python
graph = create_support_graph()
config = {"configurable": {"thread_id": "conv-123"}}

# Turn 1
state1 = create_initial_state("user_1", HumanMessage(content="Hello"))
result1 = graph.invoke(state1, config)
assert result1["last_agent"] == "fallback"

# Turn 2 (with context)
state2 = create_initial_state("user_1", HumanMessage(content="I need help with authentication"))
result2 = graph.invoke(state2, config)
assert result2["last_agent"] == "technical"
```

**Validation**:
- ✅ Thread ID persists state
- ✅ Message history accumulates
- ✅ Agents can reference prior context

---

### Milestone 3.3: Error Handling
**Duration**: 1 day

**Implementation Checklist**:
- ✅ Try-catch in all agent `__call__` methods
- ✅ Graceful degradation on tool failures
- ✅ Timeout for long-running operations

**Edge Cases**:
```python
# Test: OpenAI API error
# Simulate by setting invalid API key temporarily
# Expected: Log error + fallback response

# Test: Vector store missing
# Rename vectorstore directory
# Expected: FileNotFoundError with helpful message

# Test: Tool execution error
# Mock billing API failure
# Expected: Error message to user + case escalation
```

---

## 🌐 Phase 4: API Layer (Week 4)

### Milestone 4.1: FastAPI Endpoints
**Duration**: 2 days

**Implementation Checklist**:
- ✅ `/` - Root with API info
- ✅ `/health` - Health check
- ✅ `/chat` - Main endpoint (POST)
- ✅ `/graph` - Visualization (GET)
- ✅ `/reset` - Clear thread (POST)

**Testing**:
```bash
# Start server
python main.py &

# Test health
curl http://localhost:8000/health
# Expected: {"status":"healthy",...}

# Test chat
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Test","user_id":"test_user"}'
# Expected: {"response":"...","thread_id":"..."}
```

**Load Testing** (optional):
```bash
pip install locust
locust -f tests/load_test.py --host http://localhost:8000
```

---

### Milestone 4.2: Request/Response Validation
**Duration**: 1 day

**Implementation Checklist**:
- ✅ Pydantic models for all endpoints
- ✅ Input sanitization (XSS prevention)
- ✅ Output validation (no PII leakage)

**Testing**:
```bash
# Test invalid input
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"invalid":"data"}'
# Expected: 422 Unprocessable Entity

# Test SQL injection attempt
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"'; DROP TABLE users--","user_id":"test"}'
# Expected: Sanitized, no SQL executed
```

---

### Milestone 4.3: Logging & Monitoring
**Duration**: 1 day

**Implementation Checklist**:
- ✅ Structured JSON logging
- ✅ Request ID tracking
- ✅ Latency metrics
- ✅ Error rate tracking

**Log Sample**:
```json
{
  "timestamp": "2025-10-27T10:30:45Z",
  "level": "INFO",
  "request_id": "req-abc-123",
  "user_id": "user_12345",
  "thread_id": "thread-xyz",
  "agent": "technical",
  "action": "generate_response",
  "latency_ms": 1450,
  "status": "success"
}
```

---

## 🚀 Phase 5: Production Readiness (Week 5-6)

### Milestone 5.1: OpenSearch Migration
**Duration**: 3 days

**Tasks**:
1. Setup OpenSearch cluster (Docker or AWS)
2. Migrate embedding ingestion to OpenSearch
3. Update retriever to use OpenSearch
4. Performance comparison vs FAISS

**Commands**:
```bash
# Start OpenSearch
docker-compose up -d opensearch

# Rebuild vector store
export VECTOR_STORE_TYPE=opensearch
python retriever/build_vectorstore.py

# Test retrieval
python -c "
from retriever.retriever import get_retriever
retriever = get_retriever()
print(retriever.retrieve_context('authentication'))
"
```

**Validation**:
- ✅ All documents indexed
- ✅ Retrieval accuracy ≥ FAISS
- ✅ Latency < 500ms (p95)

---

### Milestone 5.2: PostgreSQL Checkpointer
**Duration**: 2 days

**Implementation**:
```python
from langgraph.checkpoint.postgres import PostgresSaver

# Replace MemorySaver in graph.py
checkpointer = PostgresSaver(
    connection_string="postgresql://user:pass@localhost/db"
)

graph = workflow.compile(checkpointer=checkpointer)
```

**Schema**:
```sql
CREATE TABLE conversation_checkpoints (
    thread_id VARCHAR(255) PRIMARY KEY,
    state JSONB NOT NULL,
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**Testing**:
```python
# Persistence test
state1 = graph.invoke(initial_state, config)
# Restart application
state2 = graph.invoke(continue_state, config)
# Verify state2 has history from state1
```

---

### Milestone 5.3: Real Billing Integration
**Duration**: 3 days

**Tasks**:
1. Replace mock tools with real API clients
2. Implement authentication (API keys)
3. Error handling (retries, circuit breaker)
4. Testing with staging environment

**Example**:
```python
# tools/billing_tools.py
import requests

def get_subscription(user_id: str) -> dict:
    response = requests.get(
        f"{BILLING_API_URL}/subscriptions/{user_id}",
        headers={"Authorization": f"Bearer {API_KEY}"},
        timeout=5
    )
    response.raise_for_status()
    return response.json()
```

---

### Milestone 5.4: Security Hardening
**Duration**: 2 days

**Checklist**:
- ✅ JWT authentication for `/chat`
- ✅ Rate limiting (10 req/min per user)
- ✅ Input validation (max message length: 1000 chars)
- ✅ HTTPS only (TLS 1.3)
- ✅ Secrets in AWS Secrets Manager
- ✅ CORS whitelist (no wildcard)

**Testing**:
```bash
# Test rate limiting
for i in {1..15}; do
  curl -X POST http://localhost:8000/chat -d '{"message":"test","user_id":"user"}' &
done
# Expected: 10 succeed, 5 get 429 Too Many Requests
```

---

## 📊 Phase 6: Observability (Week 7)

### Milestone 6.1: Prometheus Metrics
**Duration**: 2 days

**Metrics**:
```python
from prometheus_client import Counter, Histogram

support_requests = Counter(
    'support_requests_total',
    'Total support requests',
    ['agent', 'category']
)

support_latency = Histogram(
    'support_latency_seconds',
    'Request latency',
    ['agent']
)
```

**Grafana Dashboard**:
- Request rate (by agent)
- Latency (p50, p95, p99)
- Error rate
- Agent utilization

---

### Milestone 6.2: Distributed Tracing
**Duration**: 2 days

**Setup OpenTelemetry**:
```python
from opentelemetry import trace
from opentelemetry.exporter.jaeger import JaegerExporter

tracer = trace.get_tracer(__name__)

@tracer.start_as_current_span("technical_agent_execute")
def execute(state):
    # Agent logic
    pass
```

---

## 🧪 Phase 7: Testing & QA (Week 8)

### Milestone 7.1: Unit Tests
**Coverage Target**: >80%

```bash
pytest tests/unit/ --cov=. --cov-report=html
```

**Test Files**:
- `test_router_agent.py` (classification accuracy)
- `test_technical_agent.py` (RAG correctness)
- `test_billing_agent.py` (tool calling)
- `test_state.py` (serialization)

---

### Milestone 7.2: Integration Tests
**Scenarios**:
1. Technical → Billing switching
2. Multi-turn with context
3. Error recovery
4. Concurrent requests

---

### Milestone 7.3: User Acceptance Testing
**Test Cases**:
- 50 real customer queries
- Manual validation by domain experts
- Success rate target: >90%

---

## 🚢 Phase 8: Deployment (Week 9-10)

### Milestone 8.1: Containerization
**Duration**: 2 days

**Dockerfile**:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

**Build & Push**:
```bash
docker build -t telecom-support:v1.0 .
docker push registry.example.com/telecom-support:v1.0
```

---

### Milestone 8.2: Kubernetes Deployment
**Duration**: 3 days

**Manifests**:
- `deployment.yaml` (3 replicas)
- `service.yaml` (LoadBalancer)
- `configmap.yaml` (env vars)
- `secret.yaml` (API keys)

**Deploy**:
```bash
kubectl apply -f k8s/
kubectl get pods
# Expected: 3 pods running
```

---

### Milestone 8.3: Production Rollout
**Duration**: 3 days

**Strategy**: Blue-Green Deployment
1. Deploy v1.0 to "green" environment
2. Route 10% traffic to green
3. Monitor for 24h
4. Gradually increase to 100%
5. Decommission blue

**Rollback Plan**:
```bash
kubectl rollout undo deployment/telecom-support
```

---

## 📈 Success Metrics

### Technical KPIs
- ✅ **Uptime**: 99.9% (8.76h downtime/year)
- ✅ **Latency**: p95 < 2s
- ✅ **Error Rate**: < 0.1%
- ✅ **Classification Accuracy**: > 95%

### Business KPIs
- ✅ **Resolution Rate**: > 80% (no human escalation)
- ✅ **CSAT Score**: > 4.0 / 5.0
- ✅ **Cost Savings**: 60% reduction in support tickets

---

## 🔧 Optimizations & Enhancements

### Quick Wins (Week 11)
1. **Caching**: Redis for frequent queries (e.g., refund policy)
2. **Batch Processing**: Embed multiple queries in parallel
3. **Prompt Tuning**: A/B test system prompts

### Advanced Features (Phase 2)
1. **Sentiment Analysis**: Detect frustrated users → escalate
2. **Multilingual**: Translate queries/responses
3. **Proactive Support**: Notify users of outages
4. **Analytics Dashboard**: Query trends, common issues

---

## 🎓 Training & Documentation

### Developer Onboarding
- Architecture walkthrough (1h)
- Code review session (2h)
- Hands-on: Add a new agent (4h)

### Operations Runbook
- Deployment procedure
- Rollback steps
- Incident response playbook
- On-call rotation

---

## 🏁 Conclusion

This plan provides a **complete roadmap from prototype to production**. Each milestone has clear:
- ✅ **Deliverables**: What to build
- ✅ **Validation**: How to test
- ✅ **Duration**: Time estimate

**Total Timeline**: 10-11 weeks (2.5 months)

**Next Steps**:
1. Review plan with stakeholders
2. Allocate team resources
3. Set up project tracking (Jira/Linear)
4. Begin Phase 1 execution

---

**Questions? Contact**: [Your Email]
