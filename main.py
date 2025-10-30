"""
Telecom Support Agents - FastAPI Application

Main orchestration layer that wires:
  - OpenAI LLM initialization
  - FAISS retriever for technical documentation
  - Billing tools and agents
  - LangGraph state machine (Router → Technical/Billing/Fallback agents)
  - Multi-turn conversation session management

Environment Variables:
  MODEL_NAME          OpenAI model name (default: 'gpt-4o-mini')
  OPENAI_API_KEY      Required - OpenAI API key
  EMBEDDING_MODEL     Embedder model for retriever (default: text-embedding-3-small)

Usage:
  uvicorn main:app --reload --port 8000

Dependencies:
  - retriever/retriever.py: KBRetriever, RetrieverConfig
  - graph.py: build_graph, run_turn
  - agents/*: RouterAgent, TechnicalAgent, BillingAgent, FallbackAgent
  - tools/billing_tools.py: as_langchain_tools
"""
from __future__ import annotations

import logging
import os
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from langchain_core.language_models.chat_models import BaseChatModel

# Local imports - Core components
from retriever.retriever import KBRetriever, RetrieverConfig
from tools.billing_tools import as_langchain_tools
from agents.billing_agent import BillingAgent
from graph import build_graph, run_turn

# Load environment configuration
load_dotenv()
logger = logging.getLogger(__name__)


# ============================================================================
# Configuration
# ============================================================================

class AppConfig:
    """Application configuration from environment variables."""
    
    MODEL_NAME: str = os.getenv("MODEL_NAME", "gpt-4o-mini")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    TEMPERATURE: float = 0.0
    
    @classmethod
    def validate(cls) -> None:
        """Validate required configuration."""
        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError("OPENAI_API_KEY is required")


# ============================================================================
# LLM Factory
# ============================================================================

def init_llm() -> BaseChatModel:
    """Initialize OpenAI chat model.
    
    Returns:
        ChatOpenAI: OpenAI chat model instance.
        
    Raises:
        RuntimeError: If langchain-openai not installed or OPENAI_API_KEY not set.
    """
    try:
        from langchain_openai import ChatOpenAI
    except ImportError as e:
        raise RuntimeError("langchain-openai not installed") from e
    
    logger.info(f"Initializing OpenAI: model={AppConfig.MODEL_NAME}")
    
    return ChatOpenAI(
        model=AppConfig.MODEL_NAME,
        temperature=AppConfig.TEMPERATURE,
    )


# ============================================================================
# FastAPI Application Setup
# ============================================================================

app = FastAPI(
    title="Telecom Support AI Agents",
    description="Multi-agent support system for telecom customer issues",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Application state
class AppState:
    """Singleton application state."""
    llm: Optional[BaseChatModel] = None
    retriever: Optional[KBRetriever] = None
    graph: Optional[Any] = None
    billing_agent: Optional[BillingAgent] = None
    sessions: Dict[str, Dict[str, Any]] = {}


@app.on_event("startup")
async def startup_event() -> None:
    """Initialize application resources on startup."""
    try:
        logger.info("Starting up Telecom Support Agents...")
        
        # Validate configuration
        AppConfig.validate()
        
        # 1. Initialize LLM
        logger.info("Step 1/4: Initializing LLM...")
        AppState.llm = init_llm()
        logger.info("✓ LLM initialized")
        
        # 2. Initialize Retriever
        logger.info("Step 2/4: Loading FAISS retriever...")
        AppState.retriever = KBRetriever(RetrieverConfig())
        logger.info("✓ Retriever loaded")
        
        # 3. Initialize Billing Tools & Agent
        logger.info("Step 3/4: Setting up billing tools and agent...")
        tools = as_langchain_tools()
        if not tools:
            raise RuntimeError("LangChain tools not available. Ensure langchain >=0.2")
        AppState.billing_agent = BillingAgent(llm=AppState.llm, tools=tools)
        logger.info("✓ Billing agent initialized")
        
        # 4. Build LangGraph
        logger.info("Step 4/4: Building LangGraph state machine...")
        AppState.graph = build_graph(
            llm=AppState.llm,
            retriever=AppState.retriever,
            billing_agent=AppState.billing_agent,
        )
        logger.info("✓ Graph built")
        
        logger.info("✅ Startup complete. Ready to handle requests.")
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}", exc_info=True)
        raise


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Clean up resources on shutdown."""
    logger.info("Shutting down...")
    AppState.sessions.clear()
    logger.info("✓ Cleanup complete")


# ============================================================================
# API Request/Response Models
# ============================================================================

class ChatRequest(BaseModel):
    """Chat request payload."""
    session_id: str = Field(..., description="Session identifier for multi-turn conversations")
    message: str = Field(..., min_length=1, description="User message")
    user_id: Optional[str] = Field(None, description="Optional user ID for billing context")


class SourceReference(BaseModel):
    """Reference to a source document."""
    title: Optional[str] = None
    section: Optional[str] = None
    file: Optional[str] = None
    version: Optional[str] = None
    score: float = Field(..., ge=0.0, le=1.0)


class ChatResponse(BaseModel):
    """Chat response payload."""
    reply: str = Field(..., description="Agent response")
    route: str = Field(..., description="Which agent handled the request")
    last_agent: Optional[str] = Field(None, description="Last agent in conversation")
    sources: Optional[list[SourceReference]] = Field(None, description="Referenced sources (technical agent)")
    used_tools: Optional[list[str]] = Field(None, description="Tools used in this turn")
    state_excerpt: dict = Field(..., description="State debug info")


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/healthz", tags=["Health"])
def healthz() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
def chat(req: ChatRequest) -> ChatResponse:
    """Chat endpoint for multi-turn conversations.
    
    Args:
        req: ChatRequest with session_id, message, and optional user_id
        
    Returns:
        ChatResponse with reply, route, sources, and state debug info
        
    Raises:
        HTTPException: 503 if service not initialized
    """
    # Validate service state
    if not AppState.graph or not AppState.llm:
        logger.error("Service not initialized: graph or llm is None")
        raise HTTPException(
            status_code=503,
            detail="Service not initialized. Check logs and restart."
        )
    
    try:
        # Create or retrieve session state
        session_state = AppState.sessions.get(req.session_id)
        if session_state is None:
            logger.info(f"Creating new session: {req.session_id}")
            session_state = {"history": []}
        
        # Attach user_id if provided
        if req.user_id:
            session_state["user_id"] = req.user_id
        
        # Execute one graph turn
        logger.debug(f"Processing message for session {req.session_id}")
        new_state = run_turn(AppState.graph, session_state, req.message)
        
        # Persist updated state
        AppState.sessions[req.session_id] = new_state
        
        # Extract response components
        last_agent = new_state.get("last_agent")
        route = new_state.get("route", last_agent or "fallback")
        reply = new_state.get("reply", "")
        
        # Collect sources for technical responses
        sources = None
        if last_agent == "technical":
            raw_sources = new_state.get("last_docs", [])
            sources = [SourceReference(**src) for src in raw_sources]
        
        # Build state excerpt for debugging
        router_debug = new_state.get("_router_debug", [])
        excerpt = {
            "user_id": new_state.get("user_id"),
            "last_agent": last_agent,
            "context_flags": new_state.get("context_flags", {}),
            "router_decision": router_debug[-1] if router_debug else None,
        }
        
        logger.info(f"Response generated for session {req.session_id}: agent={last_agent}, route={route}")
        
        return ChatResponse(
            reply=reply,
            route=route,
            last_agent=last_agent,
            sources=sources,
            used_tools=None,  # Future: extract from BillingAgent execution
            state_excerpt=excerpt,
        )
    
    except Exception as e:
        logger.error(f"Error processing chat request: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error processing request"
        )
