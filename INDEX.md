# 📖 Documentation Index

Welcome to the Telecom Support AI Agents project!

This index helps you navigate the comprehensive documentation and find what you need quickly.

---

## 🚀 Getting Started

### New to the Project?
**Start here** → [`QUICKSTART.md`](QUICKSTART.md)
- 5-minute setup guide
- Installation steps
- First commands
- Common issues & solutions

### Want the Big Picture?
**Read this** → [`PROJECT_SUMMARY.md`](PROJECT_SUMMARY.md)
- What was built and why
- Key design decisions
- Cost analysis & ROI
- Next steps & recommendations

---

## 📚 Core Documentation

### 1. **System Architecture**
[`ARCHITECTURE.md`](ARCHITECTURE.md) - **READ THIS FOR**:
- Complete system design
- Component interactions
- Data flow diagrams
- Performance characteristics
- Security considerations
- Monitoring strategy

**Who should read**: Developers, architects, DevOps engineers

---

### 2. **Implementation Guide**
[`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md) - **READ THIS FOR**:
- Step-by-step build instructions
- Milestone-by-milestone breakdown
- Testing procedures
- Validation criteria
- 10-week delivery roadmap

**Who should read**: Project managers, team leads, developers

---

### 3. **Migration Guide**
[`MIGRATION_GUIDE.py`](MIGRATION_GUIDE.py) - **READ THIS FOR**:
- Python → Java migration path
- LangChain4j implementation examples
- Component mappings
- Deployment strategies
- 8-week migration timeline

**Who should read**: Java developers, solution architects

---

### 4. **README**
[`README.md`](README.md) - **READ THIS FOR**:
- Project overview
- Feature list
- Usage examples
- Project structure
- Contributing guidelines

**Who should read**: Everyone (start here after QUICKSTART)

---

## 💻 Code Documentation

### Core Files

| File | Purpose | Lines | Key Classes/Functions |
|------|---------|-------|----------------------|
| `main.py` | FastAPI server + CLI | ~250 | `chat()`, `cli_mode()` |
| `graph.py` | LangGraph orchestration | ~100 | `create_support_graph()` |
| `state.py` | Conversation state | ~60 | `ConversationState`, `create_initial_state()` |
| `config.py` | Configuration | ~40 | `Settings`, `settings` |

---

### Agent Implementations

| Agent | File | Purpose | Key Methods |
|-------|------|---------|-------------|
| **Router** | `router/router_agent.py` | Classify intent | `classify()`, `__call__()` |
| **Technical** | `agents/technical_agent.py` | RAG-based support | `answer_question()`, `__call__()` |
| **Billing** | `agents/billing_agent.py` | Tool-calling | `handle_request()`, `__call__()` |
| **Fallback** | `agents/fallback_agent.py` | Clarification | `__call__()` |

---

### Supporting Modules

| Module | File | Purpose |
|--------|------|---------|
| **Vector Store Builder** | `retriever/build_vectorstore.py` | Create FAISS index |
| **Retriever** | `retriever/retriever.py` | RAG context retrieval |
| **Billing Tools** | `tools/billing_tools.py` | Mock billing operations |

---

## 🎓 Learning Path

### **Level 1: Beginner** (Never used LangChain/LangGraph)

1. ✅ Read [`QUICKSTART.md`](QUICKSTART.md) - Get system running
2. ✅ Run `python main.py --cli` - Try conversations
3. ✅ Read [`README.md`](README.md) - Understand features
4. ✅ Review `prompts/*.txt` - See how agents are instructed
5. ✅ Read [`ARCHITECTURE.md`](ARCHITECTURE.md) Section 1-2 - Component overview

**Time Investment**: 2-3 hours  
**Output**: Can run system and understand basic flow

---

### **Level 2: Intermediate** (Some LangChain experience)

1. ✅ Read [`ARCHITECTURE.md`](ARCHITECTURE.md) - Full system design
2. ✅ Study `graph.py` - Understand state machine
3. ✅ Study `agents/technical_agent.py` - RAG implementation
4. ✅ Study `agents/billing_agent.py` - Tool-calling pattern
5. ✅ Modify `prompts/technical_system_prompt.txt` - Customize behavior
6. ✅ Add a new document to `data/docs/` - Rebuild vector store

**Time Investment**: 4-6 hours  
**Output**: Can customize and extend the system

---

### **Level 3: Advanced** (Ready to extend or migrate)

1. ✅ Read [`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md) - Build process
2. ✅ Read [`MIGRATION_GUIDE.py`](MIGRATION_GUIDE.py) - Java patterns
3. ✅ Review `PROJECT_SUMMARY.md` - Design decisions & trade-offs
4. ✅ Implement a new agent (e.g., `SalesAgent`)
5. ✅ Replace FAISS with OpenSearch (Phase 2 migration)
6. ✅ Add authentication to FastAPI endpoints

**Time Investment**: 2-3 days  
**Output**: Can architect extensions and production deployment

---

## 🔍 Quick Reference

### Configuration
- **Environment variables**: `.env` (copy from `.env.example`)
- **App settings**: `config.py`
- **System prompts**: `prompts/*.txt`

### Running the System
```bash
# CLI mode
python main.py --cli

# API server
python main.py

# Build vector store
python retriever/build_vectorstore.py

# Run examples
python examples.py
```

### API Endpoints
- `GET /` - API info
- `GET /health` - Health check
- `POST /chat` - Send message
- `GET /graph` - Visualize graph
- `POST /reset` - Clear conversation

### Testing
```bash
# Unit tests (if implemented)
pytest tests/unit/

# Integration tests (if implemented)
pytest tests/integration/

# Manual testing
python examples.py
```

---

## 📦 File Structure

```
telecom-support-ai-agents/
│
├── 📄 QUICKSTART.md           ← Start here (5-min setup)
├── 📄 PROJECT_SUMMARY.md      ← Executive overview
├── 📄 README.md               ← Full project docs
├── 📄 ARCHITECTURE.md         ← System design
├── 📄 IMPLEMENTATION_PLAN.md  ← Build roadmap
├── 📄 MIGRATION_GUIDE.py      ← Java migration
├── 📄 INDEX.md                ← You are here
│
├── 📄 main.py                 ← Entry point
├── 📄 graph.py                ← LangGraph setup
├── 📄 state.py                ← State schema
├── 📄 config.py               ← Configuration
├── 📄 examples.py             ← Usage demos
├── 📄 requirements.txt        ← Dependencies
├── 📄 setup.sh                ← Setup script
│
├── 📁 router/
│   └── router_agent.py        ← Classification
│
├── 📁 agents/
│   ├── technical_agent.py     ← RAG agent
│   ├── billing_agent.py       ← Tool-calling agent
│   └── fallback_agent.py      ← Clarification
│
├── 📁 retriever/
│   ├── build_vectorstore.py   ← Index builder
│   └── retriever.py           ← RAG retriever
│
├── 📁 tools/
│   └── billing_tools.py       ← Mock tools
│
├── 📁 prompts/
│   ├── router_system_prompt.txt
│   ├── technical_system_prompt.txt
│   └── billing_system_prompt.txt
│
└── 📁 data/
    ├── docs/                  ← Technical documentation
    │   ├── auth_faq.md
    │   ├── integration_guide.md
    │   ├── rate_limits.md
    │   └── troubleshooting_common.md
    └── vectorstore/           ← FAISS index (generated)
```

---

## 🎯 Use Case Navigation

### "I want to..."

#### ...get the system running ASAP
→ [`QUICKSTART.md`](QUICKSTART.md)

#### ...understand how it works
→ [`ARCHITECTURE.md`](ARCHITECTURE.md)

#### ...build it from scratch
→ [`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md)

#### ...migrate to Java
→ [`MIGRATION_GUIDE.py`](MIGRATION_GUIDE.py)

#### ...customize for my company
1. Replace docs in `data/docs/`
2. Edit prompts in `prompts/`
3. Update tools in `tools/billing_tools.py`
4. Run `python retriever/build_vectorstore.py`

#### ...add a new agent (e.g., Sales)
1. Create `agents/sales_agent.py`
2. Define tools in `tools/sales_tools.py`
3. Add "sales" category to router prompt
4. Update graph in `graph.py` (add node + edge)

#### ...deploy to production
→ [`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md) Phase 5-8

#### ...troubleshoot issues
→ [`QUICKSTART.md`](QUICKSTART.md) "Common Issues" section

---

## 📞 Support & Resources

### Internal Resources
- **Setup Issues**: See [`QUICKSTART.md`](QUICKSTART.md)
- **Architecture Questions**: See [`ARCHITECTURE.md`](ARCHITECTURE.md)
- **Code Understanding**: Start with `main.py` and `graph.py`

### External Resources
- **LangChain Docs**: https://python.langchain.com/docs/
- **LangGraph Guide**: https://langchain-ai.github.io/langgraph/
- **OpenAI API**: https://platform.openai.com/docs/
- **FAISS**: https://github.com/facebookresearch/faiss
- **LangChain4j** (Java): https://docs.langchain4j.dev/

### Community
- **GitHub Issues**: Report bugs or request features
- **Discussions**: Ask questions, share improvements
- **Pull Requests**: Contribute enhancements

---

## 🏆 Best Practices

### For Developers
1. ✅ Always activate virtual environment: `source venv/bin/activate`
2. ✅ Read logs: Set `LOG_LEVEL=DEBUG` in `.env` for debugging
3. ✅ Test changes: Use `python main.py --cli` for quick validation
4. ✅ Document decisions: Update relevant `.md` files when changing architecture

### For Operators
1. ✅ Monitor logs: Structured JSON in production
2. ✅ Backup vector store: Daily snapshots of `data/vectorstore/`
3. ✅ Track metrics: Request rate, latency, error rate
4. ✅ Health checks: `curl /health` every 30s

### For Product Managers
1. ✅ Track KPIs: Resolution rate, CSAT, cost per conversation
2. ✅ A/B test prompts: Iterate on system prompts for better outcomes
3. ✅ Analyze conversation logs: Find common failure patterns
4. ✅ Plan capacity: OpenAI costs scale linearly with usage

---

## 🔄 Version History

| Version | Date | Changes |
|---------|------|---------|
| **1.0** | 2025-10-27 | Initial implementation - All agents functional |
| **1.1** | TBD | Production hardening (auth, monitoring) |
| **2.0** | TBD | Java migration (LangChain4j) |

---

## 📝 License

MIT License - See LICENSE file for details

---

## 🙏 Acknowledgments

Built with:
- **LangChain** - Agent framework
- **LangGraph** - State machine orchestration
- **OpenAI** - GPT-4o-mini API
- **FAISS** - Vector similarity search
- **FastAPI** - REST API framework

---

**Last Updated**: October 27, 2025  
**Maintained By**: [Your Team]  
**Questions?** Create an issue on GitHub

---

## Quick Links

📖 [QUICKSTART](QUICKSTART.md) | 🏗️ [ARCHITECTURE](ARCHITECTURE.md) | 📋 [IMPLEMENTATION PLAN](IMPLEMENTATION_PLAN.md) | 🔄 [MIGRATION GUIDE](MIGRATION_GUIDE.py) | 📊 [PROJECT SUMMARY](PROJECT_SUMMARY.md)
