"""
LangGraph Orchestration.
Defines the conversation graph with conditional routing between agents.

Design principle: State machine with explicit edges for maintainability.
Easy to visualize and port to Java/LangChain4j.
"""
import logging
from typing import Literal

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from state import ConversationState
from router.router_agent import RouterAgent
from agents.technical_agent import TechnicalAgent
from agents.billing_agent import BillingAgent
from agents.fallback_agent import FallbackAgent

logger = logging.getLogger(__name__)


def create_support_graph():
    """
    Build the LangGraph for multi-agent customer support.
    
    Graph structure:
        START → router → [technical|billing|fallback] → END
    
    Returns:
        Compiled StateGraph ready for execution
    """
    
    # Initialize agents
    router = RouterAgent()
    technical = TechnicalAgent()
    billing = BillingAgent()
    fallback = FallbackAgent()
    
    # Create graph
    workflow = StateGraph(ConversationState)
    
    # Add nodes
    workflow.add_node("router", router)
    workflow.add_node("technical", technical)
    workflow.add_node("billing", billing)
    workflow.add_node("fallback", fallback)
    
    # Set entry point
    workflow.set_entry_point("router")
    
    # Define routing logic
    def route_to_agent(state: ConversationState) -> Literal["technical", "billing", "fallback"]:
        """
        Conditional edge: route based on classification.
        
        Args:
            state: Current conversation state
        
        Returns:
            Next node name to execute
        """
        category = state.get("current_category", "other")
        
        if category == "technical":
            logger.info("→ Routing to technical agent")
            return "technical"
        elif category == "billing":
            logger.info("→ Routing to billing agent")
            return "billing"
        else:
            logger.info("→ Routing to fallback agent")
            return "fallback"
    
    # Add conditional edges from router
    workflow.add_conditional_edges(
        "router",
        route_to_agent,
        {
            "technical": "technical",
            "billing": "billing",
            "fallback": "fallback"
        }
    )
    
    # All agents go to END
    workflow.add_edge("technical", END)
    workflow.add_edge("billing", END)
    workflow.add_edge("fallback", END)
    
    # Add memory (for conversation persistence)
    memory = MemorySaver()
    
    # Compile graph
    app = workflow.compile(checkpointer=memory)
    
    logger.info("✓ Support graph compiled successfully")
    
    return app


# Visualization helper (optional)
def visualize_graph(graph):
    """
    Generate Mermaid diagram of the graph structure.
    
    Args:
        graph: Compiled StateGraph
    
    Returns:
        Mermaid diagram as string
    """
    try:
        return graph.get_graph().draw_mermaid()
    except Exception as e:
        logger.warning(f"Could not generate graph visualization: {e}")
        return None
