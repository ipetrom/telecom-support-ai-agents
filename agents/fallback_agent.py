"""
Fallback Agent: Handles unclear requests and prompts clarification.

Design principle: Simple, deterministic response for "other" category.
No LLM needed - just a template response.
"""
import logging

from langchain_core.messages import AIMessage

from state import ConversationState

logger = logging.getLogger(__name__)


class FallbackAgent:
    """
    Handles messages that don't fit technical or billing categories.
    
    Design notes:
    - Deterministic response (no LLM call needed)
    - Sets needs_clarification flag for router to re-classify next turn
    - Cost-effective for greetings and unclear inputs
    """
    
    def __init__(self):
        self.clarification_prompt = (
            "Hello! I'm a specialist in technical support and billing. "
            "I can help with:\n\n"
            "🔧 **Technical Support**: Service configuration, connectivity issues, "
            "API integration, authentication, troubleshooting\n\n"
            "💳 **Billing Support**: Payments, refunds, subscription plans, "
            "invoices, pricing questions\n\n"
            "What exactly do you need help with today?"
        )
    
    def __call__(self, state: ConversationState) -> ConversationState:
        """
        LangGraph node function: request clarification.
        
        Args:
            state: Current conversation state
        
        Returns:
            Updated state with clarification prompt
        """
        logger.info("Fallback agent activated - requesting clarification")
        
        # Add clarification message
        state["messages"].append(
            AIMessage(content=self.clarification_prompt)
        )
        
        # Set flag for next turn
        state["needs_clarification"] = True
        state["last_agent"] = "fallback"
        
        logger.info(f"Fallback agent updated state (message count: {len(state['messages'])})")
        
        return state
