"""
TechnicalAgent — grounded answers from local KB (RAG) with zero‑hallucination guardrails.

Responsibilities
- Answer only using retrieved context from local docs (01–04).
- If insufficient context (< min_hits or low scores) -> ask for clarification (NO_CONTEXT).
- Always cite sources as: Title — Section — File (version).
- Keep replies compact and actionable: short answer + optional steps + verification.

Integration
  from retriever.retriever import load_retriever, RetrieverConfig
  from agents.technical_agent import TechnicalAgent

  retr = load_retriever(RetrieverConfig(artifacts_dir=Path("artifacts")))
  llm = init_llm()  # any chat model
  agent = TechnicalAgent(llm=llm, retriever=retr)
  out = agent.run(state, user_message)

State contract (minimal)
- state.history: list[dict] with keys {"role": "user"|"assistant", "content": str}
- state.last_docs: optional cache of last sources
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from retriever.retriever import KBRetriever


SYSTEM_PROMPT = (
    "You are TechnicalAgent. Answer ONLY using the provided CONTEXT chunks from the local Knowledge Base.\n"
    "If the context is insufficient or unrelated, say so and ask for precise clarification (model/device, access type FTTH/DSL/LTE/5G, symptoms).\n"
    "Rules:\n"
    "- Be concise and actionable.\n"
    "- Never invent facts beyond the CONTEXT.\n"
    "- Always include a 'Sources' section listing Title — Section — File (version).\n"
    "- If NO_CONTEXT: ask for 1–2 clarifying details and mention what's missing.\n"
)


@dataclass
class ConversationState:
    history: List[Dict[str, str]] = field(default_factory=list)
    last_docs: List[Dict[str, Any]] = field(default_factory=list)


def _compose_context(sources: List[Dict[str, Any]], max_chars: int = 8000) -> str:
    # Compose a textual context block from retriever Documents; trim to budget
    parts: List[str] = []
    used = 0
    for s in sources:
        doc = s.get("doc")
        meta = getattr(doc, "metadata", {})
        header = f"[SOURCE] {meta.get('title')} — {' / '.join(meta.get('section_path', [])) or '-'} — {meta.get('path')} (v:{meta.get('version')})"
        body = getattr(doc, "page_content", "").strip()
        chunk = header + "\n" + body + "\n"
        if used + len(chunk) > max_chars:
            break
        parts.append(chunk)
        used += len(chunk)
    return "\n\n".join(parts)


def _format_sources(sources: List[Dict[str, Any]]) -> str:
    lines = []
    for s in sources:
        m = getattr(s.get("doc"), "metadata", {})
        title = m.get("title")
        section = " / ".join(m.get("section_path", [])) or "-"
        file = (m.get("path") or "").split("/")[-1]
        version = m.get("version") or ""
        lines.append(f"- {title} — {section} — {file} ({version})")
    return "\n".join(lines)


class TechnicalAgent:
    def __init__(self, llm: BaseChatModel, retriever: KBRetriever):
        self.llm = llm
        self.retriever = retriever

    def run(self, state: ConversationState, user_message: str) -> Dict[str, Any]:
        # Retrieve
        ret = self.retriever.retrieve(user_message)
        docs = ret["docs"]
        # wrap docs with meta for formatting later
        source_wrapped = [{"doc": d, "score": s} for d, s in zip(docs, ret["scores"])]

        if ret["no_context"] or not docs:
            # Ask for clarification; cite nothing (no solid sources)
            reply = (
                "I couldn't find enough information in the knowledge base to answer confidently. "
                "Please share these details so I can help: device/router model, access type (FTTH/DSL/LTE/5G), "
                "and a short description of symptoms (e.g., PON LED blinking, no internet on 5 GHz)."
            )
            return {"reply": reply, "sources": [], "no_context": True}

        # Build context and query LLM
        context_text = _compose_context(source_wrapped)
        sources_block = _format_sources(source_wrapped)

        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=(
                "CONTEXT (from local KB):\n" + context_text + "\n\n" +
                "QUESTION:\n" + user_message + "\n\n" +
                "Respond concisely. If there are steps, put them under 'Steps'. Always add 'Sources'."
            )),
        ]
        ai = self.llm.invoke(messages)
        text = ai.content if isinstance(ai, AIMessage) else str(ai)

        # Ensure Sources are appended (in case the model forgot)
        if "Sources:" not in text:
            text = text.rstrip() + "\n\nSources:\n" + sources_block
        else:
            # Replace a placeholder [SOURCES] if present
            text = text.replace("[SOURCES]", "\n" + sources_block)

        # Save last sources in state-friendly structure
        friendly_sources = [
            {
                "title": d.metadata.get("title"),
                "section": " / ".join(d.metadata.get("section_path", [])) or None,
                "file": (d.metadata.get("path") or "").split("/")[-1],
                "version": d.metadata.get("version"),
                "score": s,
            }
            for d, s in zip(docs, ret["scores"])
        ]

        return {
            "reply": text,
            "sources": friendly_sources,
            "no_context": False,
        }
