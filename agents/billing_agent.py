"""
BillingAgent — tool-calling specialist for billing topics.

Responsibilities
- Handle: plan/price confirmation, refund requests, refund policy explanation.
- Use tools from tools.billing_tools: get_subscription, open_refund_case, get_refund_policy.
- Keep replies concise and actionable. Never expose raw PIIs. Currency PLN.
- Must support multi‑turn: preserve conversation history (passed in `state`).

Dependencies
  langchain-core >= 0.2
  (optional) langchain-openai or other chat LLM provider supporting tool calling

Typical usage (inside your graph node):

    from tools.billing_tools import as_langchain_tools
    from agents.billing_agent import BillingAgent

    tools = as_langchain_tools()  # StructuredTool[]
    llm = init_llm()              # any chat model with tool calling, e.g. ChatOpenAI(...)
    agent = BillingAgent(llm=llm, tools=tools)

    result = agent.run(state, user_message)
    # result: {"reply": str, "used_tools": [...], "updates": {"billing_case_id": "R10001"}}

State contract (minimal)
- state.history: list[dict] with keys {"role": "user"|"assistant", "content": str}
- state.user_id: str | None
- state.context_flags: dict (may include: {"refund_in_progress": bool})
- The agent does not mutate storage; it returns `updates` to be merged by the graph.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import BaseTool


SYSTEM_PROMPT = (
    "You are BillingAgent, a precise, helpful billing specialist.\n"
    "Scope: confirm subscription plan & price; explain refund policy; open refund cases.\n"
    "Rules:\n"
    "- Use tools when needed. Ask for missing fields (user_id, reason, amount, invoice_id)\n"
    "  before opening a refund case.\n"
    "- Keep answers concise (<= 6 sentences) and list clear next steps.\n"
    "- Currency is PLN. Do not invent data.\n"
    "- If the request is outside billing scope, say so briefly and return control to router.\n"
)


@dataclass
class ConversationState: #lokalna pamięć rozmowy
    history: List[Dict[str, str]] = field(default_factory=list)
    user_id: Optional[str] = None
    context_flags: Dict[str, Any] = field(default_factory=dict)


class BillingAgent:
    def __init__(self, llm: BaseChatModel, tools: List[BaseTool]):
        self.llm = llm.bind_tools(tools)
        self.tools = {t.name: t for t in tools}

    # ---- public API ----
    def run(self, state: ConversationState, user_message: str) -> Dict[str, Any]:
        """Run one billing turn using tool-calling if necessary.
        Returns { reply, used_tools, updates }.
        """
        messages = [SystemMessage(content=SYSTEM_PROMPT)]
        # Rehydrate short history (last 6 turns max)
        for m in state.history[-12:]: #ostatnie 12 wiadomości (6 tur)
            role = m.get("role", "user")
            content = m.get("content", "")
            if role == "user":
                messages.append(HumanMessage(content=content))
            else:
                messages.append(AIMessage(content=content))
        # Current user input
        if state.user_id:
            user_message = f"[user_id={state.user_id}] " + user_message #dodanie user_id do wiadomości
        messages.append(HumanMessage(content=user_message))

        # First LLM pass (may return tool calls)
        ai = self.llm.invoke(messages)
        used_tools: List[Dict[str, Any]] = []

        if getattr(ai, "tool_calls", None):
            # Execute tools sequentially and feed results back
            intermediate: List[Any] = []
            tool_messages: List[ToolMessage] = []
            for call in ai.tool_calls:
                name = call["name"]
                args = call.get("args", {})
                tool = self.tools.get(name)
                if not tool:
                    # Unknown tool — reply safely
                    continue
                try:
                    out = tool.invoke(args)
                except Exception as e:
                    out = {"error": str(e)}
                used_tools.append({"name": name, "args": args, "output": out})
                # Send back ToolMessage
                tool_messages.append(ToolMessage(tool_call_id=call["id"], content=str(out)))
            # Summarize tool outputs to final user reply
            messages.extend([ai, *tool_messages])
            final = self.llm.invoke(messages)
            reply_text = final.content if isinstance(final, AIMessage) else str(final)
        else:
            # No tool calls — direct answer (policy explanation etc.)
            reply_text = ai.content if isinstance(ai, AIMessage) else str(ai)

        updates: Dict[str, Any] = {}
        # Heuristic: if we opened a refund case, try to read case_id from tool outputs
        for t in used_tools:
            if t["name"] == "open_refund_case" and isinstance(t.get("output"), dict):
                case_id = t["output"].get("case_id")
                if case_id:
                    updates.setdefault("billing_case_id", case_id)
                    updates.setdefault("context_flags", {}).update({"refund_in_progress": True})

        return {"reply": reply_text, "used_tools": used_tools, "updates": updates}