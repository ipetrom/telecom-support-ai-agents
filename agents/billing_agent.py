"""
Billing Agent: Handles billing inquiries with tool-calling.

Design principle: Function-calling for structured actions.
Uses OpenAI's native tool support for reliability.
"""
import logging
from typing import List

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage
from langchain_core.tools import tool

from config import settings
from state import ConversationState
from tools.billing_tools import (
    get_subscription,
    open_refund_case,
    get_refund_policy
)

logger = logging.getLogger(__name__)


# Wrap tools with LangChain decorator for type safety
@tool
def get_subscription_tool(user_id: str) -> dict:
    """Retrieve current subscription plan and billing details for a user."""
    return get_subscription(user_id)


@tool
def open_refund_case_tool(user_id: str, reason: str, amount: float = None) -> dict:
    """Create a refund case in the billing system. Requires user_id and reason."""
    return open_refund_case(user_id, reason, amount)


@tool
def get_refund_policy_tool() -> str:
    """Get the complete refund policy document."""
    return get_refund_policy()


class BillingAgent:
    """
    Billing specialist agent with tool-calling capabilities.
    
    Design notes:
    - Uses OpenAI function calling for structured tool invocation
    - Automatically handles tool execution loop
    - User ID injected from state for security
    """
    
    def __init__(self):
        self.tools = [
            get_subscription_tool,
            open_refund_case_tool,
            get_refund_policy_tool
        ]
        
        self.llm = ChatOpenAI(
            model=settings.openai_model,
            temperature=settings.temperature,
            openai_api_key=settings.openai_api_key
        ).bind_tools(self.tools)
        
        self.system_prompt = self._load_system_prompt()
    
    def _load_system_prompt(self) -> str:
        """Load billing agent system prompt from file."""
        prompt_path = "./prompts/billing_system_prompt.txt"
        try:
            with open(prompt_path, "r") as f:
                return f.read().strip()
        except FileNotFoundError:
            logger.error(f"Billing system prompt not found at {prompt_path}")
            return "You are a billing specialist. Use available tools to help users with billing inquiries."
    
    def _execute_tool_call(self, tool_call, user_id: str) -> dict:
        """
        Execute a tool call with user_id injection.
        
        Args:
            tool_call: The tool call object from LLM
            user_id: User ID from state (for security/context)
        
        Returns:
            Tool execution result
        """
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        
        logger.info(f"Executing tool: {tool_name} with args: {tool_args}")
        
        # Inject user_id for tools that need it
        if tool_name == "get_subscription_tool":
            result = get_subscription_tool.invoke({"user_id": user_id})
        elif tool_name == "open_refund_case_tool":
            result = open_refund_case_tool.invoke({
                "user_id": user_id,
                "reason": tool_args.get("reason"),
                "amount": tool_args.get("amount")
            })
        elif tool_name == "get_refund_policy_tool":
            result = get_refund_policy_tool.invoke({})
        else:
            result = {"error": f"Unknown tool: {tool_name}"}
        
        logger.info(f"Tool result: {str(result)[:200]}...")
        return result
    
    def handle_request(self, user_message: str, user_id: str) -> str:
        """
        Process billing request with tool calling.
        
        Args:
            user_message: User's billing question/request
            user_id: User identifier for tool calls
        
        Returns:
            Agent response as string
        """
        logger.info(f"Billing agent handling request: {user_message[:100]}...")
        
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=user_message)
        ]
        
        # Tool calling loop
        max_iterations = 5
        for iteration in range(max_iterations):
            response = self.llm.invoke(messages)
            
            # Check if LLM wants to call tools
            if not response.tool_calls:
                # No more tool calls - return final answer
                logger.info(f"✓ Billing agent responded ({len(response.content)} chars)")
                return response.content
            
            # Execute tool calls
            messages.append(response)
            
            for tool_call in response.tool_calls:
                result = self._execute_tool_call(tool_call, user_id)
                
                # Add tool result to conversation
                tool_message = ToolMessage(
                    content=str(result),
                    tool_call_id=tool_call["id"]
                )
                messages.append(tool_message)
        
        # Fallback if max iterations reached
        logger.warning("Max tool iterations reached")
        return "I've gathered the information, but let me summarize: Could you clarify what specific billing action you need?"
    
    def __call__(self, state: ConversationState) -> ConversationState:
        """
        LangGraph node function: handle billing request.
        
        Args:
            state: Current conversation state
        
        Returns:
            Updated state with agent response
        """
        # Get the last user message
        last_message = state["messages"][-1]
        user_request = last_message.content
        user_id = state["user_id"]
        
        # Generate response with tool calling
        answer = self.handle_request(user_request, user_id)
        
        # Update state
        state["messages"].append(AIMessage(content=answer))
        state["last_agent"] = "billing"
        
        logger.info(f"Billing agent updated state (message count: {len(state['messages'])})")
        
        return state
