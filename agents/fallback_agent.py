"""
FallbackAgent — polite clarification + handoff.

Responsibilities
- Handle messages classified as "other" or when a specialist agent signals out-of-scope.
- Ask concise, targeted clarification to route the user to Technical or Billing agents.
- Keep replies short (<= 4 sentences) and propose examples the user can choose from.

Integration
  from agents.fallback_agent import FallbackAgent, ConversationState
  agent = FallbackAgent()
  out = agent.run(state, user_message)

State contract (minimal)
- state.history: list[dict] {role: 'user'|'assistant', content: str}
- state.last_agent: Optional[str] ('technical'|'billing'|'fallback')
- returns: {reply: str, route_hint: Optional[str]}
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ConversationState:
    history: List[Dict[str, str]] = field(default_factory=list)
    last_agent: Optional[str] = None


_TEMPLATE = (
    "I'm a specialist in technical support and billing. "
    "I can help with service setup, technical issues, or payments/invoices.\n"
    "Please clarify what you need (choose one option or add your own):\n"
    "• [TECH] Internet drops / no internet / APN / Wi-Fi / bridge on ONT\n"
    "• [BILLING] Plan & price / invoice / refund / case status\n"
    "• [OTHER] Describe briefly — I'll route you to the right team."
)


class FallbackAgent:
    def run(self, state: ConversationState, user_message: str) -> Dict[str, Any]:
        hint = self._infer_route_hint(user_message)
        reply = _TEMPLATE
        return {"reply": reply, "route_hint": hint}

    @staticmethod
    def _infer_route_hint(text: str) -> Optional[str]:
        t = (text or "").lower()
        tech_kw = ["wifi", "wi-fi", "apn", "pon", "router", "bridge", "internet", "5g", "lte", "dsl", "ftth", "cgnat"]
        bill_kw = ["invoice", "faktura", "refund", "zwrot", "plan", "cena", "opłata", "billing"]
        if any(k in t for k in tech_kw):
            return "technical"
        if any(k in t for k in bill_kw):
            return "billing"
        return None