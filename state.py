"""
Conversation State Management.
Defines the shared state structure that flows through the LangGraph.

Design principle: Keep state minimal and serializable for Java migration.
"""
from typing import TypedDict, List, Literal, Optional, Annotated
from langchain_core.messages import BaseMessage
import operator


class ConversationState(TypedDict):
    """
    Shared state across all agents in the graph.
    
    Design notes:
    - Uses TypedDict for clear schema definition
    - All fields are JSON-serializable for language-agnostic portability
    - The 'messages' field uses operator.add for message accumulation
    """
    
    # Message history (accumulated across turns)
    messages: Annotated[List[BaseMessage], operator.add]
    
    # User identification
    user_id: str
    
    # Routing information
    current_category: Optional[Literal["technical", "billing", "other"]] = None
    last_agent: Optional[str] = None  # For audit trail
    
    # Context flags (for agent decision-making)
    needs_clarification: bool = False
    retrieved_context: Optional[str] = None  # For technical agent
    
    # Metadata
    turn_count: int = 0
    
    
def create_initial_state(user_id: str, initial_message: BaseMessage) -> ConversationState:
    """
    Factory function to create a fresh conversation state.
    
    Args:
        user_id: Unique identifier for the user
        initial_message: The first message from the user
    
    Returns:
        A properly initialized ConversationState
    """
    return ConversationState(
        messages=[initial_message],
        user_id=user_id,
        current_category=None,
        last_agent=None,
        needs_clarification=False,
        retrieved_context=None,
        turn_count=0
    )
