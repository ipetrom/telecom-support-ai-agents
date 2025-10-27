# 🚀 Quick Start Guide

Get the Telecom Support AI system running in **5 minutes**.

---

## Prerequisites

- **Python 3.10+**
- **OpenAI API Key** ([Get one here](https://platform.openai.com/api-keys))
- **10 minutes**

---

## Installation

### Step 1: Clone & Setup

```bash
# Clone repository
git clone https://github.com/ipetrom/telecom-support-ai-agents.git
cd telecom-support-ai-agents

# Run automated setup
chmod +x setup.sh
./setup.sh
```

The setup script will:
1. ✅ Create virtual environment
2. ✅ Install dependencies
3. ✅ Create `.env` file
4. ✅ Build vector store

### Step 2: Configure API Key

Edit `.env`:
```bash
OPENAI_API_KEY=sk-your-actual-key-here
```

### Step 3: Verify Installation

```bash
# Activate environment
source venv/bin/activate

# Test import
python -c "from config import settings; print('✅ Configuration loaded')"

# Check vector store
ls data/vectorstore/
# Should show: index.faiss, index.pkl
```

---

## Running the System

### Option A: Interactive CLI (Recommended for Testing)

```bash
python main.py --cli
```

**Example Session**:
```
🤖 Telecom Support AI - CLI Mode
You: How do I authenticate with your API?
🤖 Agent (technical): According to our Integration Guide, OAuth authentication requires...

You: What's my current plan?
🤖 Agent (billing): You're on the Premium 5G plan at $89.99/month...

You: quit
```

---

### Option B: REST API Server

```bash
python main.py
```

Server starts at: **http://localhost:8000**

**API Documentation**: http://localhost:8000/docs

---

## Testing API Endpoints

### Health Check
```bash
curl http://localhost:8000/health
```

**Response**:
```json
{
  "status": "healthy",
  "model": "gpt-4o-mini",
  "vectorstore": "faiss"
}
```

---

### Send Message
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "My API keeps timing out",
    "user_id": "test_user"
  }'
```

**Response**:
```json
{
  "response": "Based on our troubleshooting guide...",
  "thread_id": "abc-123-xyz",
  "agent": "technical",
  "category": "technical"
}
```

---

### Multi-Turn Conversation
```bash
# First message
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello","user_id":"user_123"}'
# Save the thread_id from response

# Follow-up (use same thread_id)
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message":"I need help with authentication",
    "user_id":"user_123",
    "thread_id":"<thread_id_from_above>"
  }'
```

---

## Example Conversations

### 🔧 Technical Support

**Query**: "How do I configure rate limiting?"

**Response**: 
```
According to our Rate Limits documentation, you can configure
rate limiting by setting the X-RateLimit-Policy header in your
API requests. The default limit is 1000 requests per hour...
```

---

### 💳 Billing Support

**Query**: "I want a refund for last month"

**Response**:
```
I'd be happy to help with a refund request. Could you please
provide the reason for the refund? For example:
- Service outage
- Billing error
- Dissatisfaction with service

Once I have this information, I'll create a case for you.
```

**Follow-up**: "There was a 3-day service outage"

**Response**:
```
✅ Refund case REF-1001 has been created for $89.99.
Status: Pending
Estimated resolution: 5-7 business days

You'll receive an email update once processed.
```

---

### ❓ Fallback Handling

**Query**: "Hello"

**Response**:
```
Hello! I'm a specialist in technical support and billing.
I can help with:

🔧 Technical Support: Service configuration, connectivity issues,
   API integration, authentication, troubleshooting

💳 Billing Support: Payments, refunds, subscription plans,
   invoices, pricing questions

What exactly do you need help with today?
```

---

## Common Issues & Solutions

### Issue: "Import langchain_openai could not be resolved"

**Solution**: Dependencies not installed
```bash
pip install -r requirements.txt
```

---

### Issue: "Vector store not found"

**Solution**: Run vector store builder
```bash
python retriever/build_vectorstore.py
```

---

### Issue: "OpenAI API error: Incorrect API key"

**Solution**: Check `.env` file
```bash
cat .env | grep OPENAI_API_KEY
# Should show: OPENAI_API_KEY=sk-...
```

---

### Issue: "Rate limit exceeded"

**Solution**: You've hit OpenAI's rate limit. Wait 60 seconds or upgrade plan.

---

## Project Structure

```
telecom-support-ai-agents/
├── 📄 main.py              # FastAPI app + CLI entry point
├── 📄 graph.py             # LangGraph orchestration
├── 📄 state.py             # Conversation state schema
├── 📄 config.py            # Configuration management
│
├── 📁 router/
│   └── router_agent.py     # Message classification
│
├── 📁 agents/
│   ├── technical_agent.py  # RAG-based technical support
│   ├── billing_agent.py    # Tool-calling billing agent
│   └── fallback_agent.py   # Clarification handler
│
├── 📁 retriever/
│   ├── build_vectorstore.py
│   └── retriever.py
│
├── 📁 tools/
│   └── billing_tools.py
│
├── 📁 prompts/
│   ├── router_system_prompt.txt
│   ├── technical_system_prompt.txt
│   └── billing_system_prompt.txt
│
└── 📁 data/
    └── docs/              # Technical documentation
```

---

## Next Steps

### 1. Explore the Code
```bash
# Open in VS Code
code .

# Read architecture
cat ARCHITECTURE.md
```

### 2. Customize System Prompts
Edit files in `prompts/` to change agent behavior.

### 3. Add Technical Documentation
Place new `.md` files in `data/docs/`, then:
```bash
python retriever/build_vectorstore.py
```

### 4. Extend with New Agent
See `IMPLEMENTATION_PLAN.md` for adding agents like `SalesAgent`.

---

## Documentation

| Document | Description |
|----------|-------------|
| **README.md** | Full project documentation |
| **ARCHITECTURE.md** | System design & components |
| **IMPLEMENTATION_PLAN.md** | Step-by-step build guide |
| **MIGRATION_GUIDE.py** | Python → Java migration |
| **examples.py** | Usage examples & demos |

---

## Support

- **Issues**: [GitHub Issues](https://github.com/ipetrom/telecom-support-ai-agents/issues)
- **Email**: support@example.com
- **Docs**: See `README.md` and `ARCHITECTURE.md`

---

## License

MIT License - see LICENSE file

---

## Tips & Tricks

### Faster Startup
```bash
# Skip vector store rebuild if unchanged
python main.py
```

### Debug Mode
```bash
export LOG_LEVEL=DEBUG
python main.py --cli
```

### Custom Port
```bash
# Edit main.py, line 262
uvicorn.run(app, host="0.0.0.0", port=9000)
```

### Production Deployment
See `IMPLEMENTATION_PLAN.md` Phase 8 for Kubernetes setup.

---

## Demo Script

**For stakeholder demonstrations**:

```bash
# Terminal 1: Start server
python main.py

# Terminal 2: Run demo
python examples.py
```

This shows 5 conversation scenarios:
1. Technical support
2. Billing support
3. Fallback handling
4. Multi-turn conversation
5. Agent switching

---

🎉 **You're all set!** Run `python main.py --cli` to start chatting.
