"""
RouterAgent — intelligent intent classification using LLM + semantic understanding.

Responsibilities
- Analyze every incoming user message to determine intent.
- Classify into: technical, billing, or unknown using LLM.
- Support synonyms and conversational variations (e.g., "moja sieć słaba" = technical).
- Route to appropriate specialist agent (TechnicalAgent, BillingAgent, FallbackAgent).
- Return confidence score for routing decisions.

Key difference from FallbackAgent:
- RouterAgent: Initial classification on EVERY message (intelligent routing)
- FallbackAgent: Handles only unclear/out-of-scope cases (asks for clarification)

Integration
  from router.router_agent import RouterAgent, ConversationState
  from langchain_openai import ChatOpenAI
  
  llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
  router = RouterAgent(llm=llm)
  result = router.route(state, user_message)

State contract (minimal)
- state.history: list[dict] {role: 'user'|'assistant', content: str}
- state.last_agent: optional, used for bias in ambiguous cases
- returns: {route: "technical"|"billing"|"fallback", confidence: float, classification: dict}
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage


@dataclass
class ConversationState:
    history: List[Dict[str, str]] = field(default_factory=list)
    last_agent: Optional[str] = None  # 'technical' | 'billing' | 'fallback'


# System prompt for intelligent intent classification
_SYSTEM_PROMPT = """You are an expert intent classifier for a telecom support system.
Your task is to analyze user messages and determine their intent with semantic understanding.

Categories:
1. **technical** — Issues or questions about: internet connectivity, Wi-Fi/router, network access (5G/LTE/DSL/FTTH), APN settings, bridge configuration, ONT troubleshooting, latency, packet loss, signal strength, device setup, connection issues, etc.
   Examples: "internet is down", "Wi-Fi won't connect", "router keeps rebooting", "moja sieć słaba", "problem z łącznością", "can't connect to 5G", "internet drops during calls"

2. **billing** — Issues or questions about: invoices, payments, subscription plans, pricing, refunds, account status, charges, payment history, contract details, service costs, etc.
   Examples: "why was I charged?", "refund request", "ile kosztuje plan", "faktura za miesiąc", "status mojej sprawy", "check my invoice", "how much is the monthly fee?"

3. **unknown** — Anything that doesn't fit the above categories or is ambiguous.
   Examples: "hello", "who are you?", "tell me a joke", "general company info", "do you have a phone number?"

Rules:
- Be flexible with synonyms, slang, colloquialisms, and non-technical language (including Polish and English mix).
- Consider context and related terms (e.g., "no internet" → technical, "plan cost" → billing, "connection issue" → technical).
- If ambiguous or doesn't fit clearly, use "unknown" category.
- Support multi-language: Polish, English, or mixed.
- Always respond with valid JSON.

Respond ONLY in JSON format (no additional text):
{
  "category": "technical" | "billing" | "unknown",
  "confidence": <float 0.0-1.0>,
  "reasoning": "<brief explanation in English>"
}"""


class RouterAgent:
    def __init__(self, llm: BaseChatModel):
        """
        Initialize RouterAgent with an LLM for semantic intent classification.
        
        Args:
            llm: A LangChain BaseChatModel (e.g., ChatOpenAI)
        """
        self.llm = llm

    def route(self, state: ConversationState, user_message: str) -> Dict[str, Any]:
        """
        Classify user intent and return routing decision.
        
        Args:
            state: ConversationState with conversation history
            user_message: User's message to classify
            
        Returns:
            {
                "route": "technical" | "billing" | "fallback",
                "confidence": float (0.0-1.0),
                "classification": {
                    "category": str,
                    "confidence": float,
                    "reasoning": str
                }
            }
        """
        classification = self._classify_intent(user_message)
        
        category = classification.get("category", "unknown")
        confidence = classification.get("confidence", 0.0)
        
        # Route based on classification
        if confidence >= 0.7 and category in ["technical", "billing"]:
            route = category
        else:
            # Low confidence or unknown intent: send to fallback
            route = "fallback"
        
        return {
            "route": route,
            "confidence": confidence,
            "classification": classification
        }

    def _classify_intent(self, user_message: str) -> Dict[str, Any]:
        """
        Use LLM to classify user intent with semantic understanding.
        
        Args:
            user_message: User's message
            
        Returns:
            {
                "category": "technical" | "billing" | "unknown",
                "confidence": float,
                "reasoning": str
            }
        """
        messages = [
            SystemMessage(content=_SYSTEM_PROMPT),
            HumanMessage(content=user_message)
        ]
        
        try:
            response = self.llm.invoke(messages)
            response_text = response.content.strip()
            
            # Parse JSON response
            classification = json.loads(response_text)
            
            # Validate and ensure required fields
            return {
                "category": str(classification.get("category", "unknown")).lower(),
                "confidence": float(classification.get("confidence", 0.0)),
                "reasoning": str(classification.get("reasoning", ""))
            }
        except (json.JSONDecodeError, ValueError, AttributeError, KeyError) as e:
            # Fallback to unknown if LLM response is malformed
            return {
                "category": "unknown",
                "confidence": 0.0,
                "reasoning": f"Classification error: {str(e)}"
            }