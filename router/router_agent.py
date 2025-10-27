"""
Router Agent: Classifies user intent into categories.

Design principle: Lightweight classification using structured output.
Uses OpenAI's JSON mode for reliable parsing.
"""
import logging
from typing import Literal

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

from config import settings
from state import ConversationState

logger = logging.getLogger(__name__)


class RouteClassification(BaseModel):
    """Schema for router output."""
    category: Literal["technical", "billing", "other"] = Field(
        description="The classified category of the user's message"
    )


class RouterAgent:
    """
    Classifies user messages into routing categories.
    
    Design notes:
    - Stateless for simplicity (can be parallelized)
    - Uses structured output for reliability
    - System prompt loaded from file for easy tuning
    """
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.openai_model,
            temperature=0.0,  # Deterministic classification
            openai_api_key=settings.openai_api_key
        )
        self.parser = JsonOutputParser(pydantic_object=RouteClassification)
        self.system_prompt = self._load_system_prompt()
    
    def _load_system_prompt(self) -> str:
        """Load router system prompt from file."""
        prompt_path = "./prompts/router_system_prompt.txt"
        try:
            with open(prompt_path, "r") as f:
                return f.read().strip()
        except FileNotFoundError:
            logger.error(f"Router system prompt not found at {prompt_path}")
            # Fallback inline prompt
            return "Classify user message as: technical, billing, or other. Return JSON: {\"category\": \"<category>\"}"
    
    def classify(self, user_message: str) -> str:
        """
        Classify a user message into a category.
        
        Args:
            user_message: The user's input text
        
        Returns:
            Category string: "technical", "billing", or "other"
        """
        logger.info(f"Classifying message: {user_message[:100]}...")
        
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=user_message)
        ]
        
        try:
            # Use JSON mode for structured output
            response = self.llm.invoke(
                messages,
                response_format={"type": "json_object"}
            )
            
            parsed = self.parser.parse(response.content)
            category = parsed["category"]
            
            logger.info(f"✓ Classified as: {category}")
            return category
            
        except Exception as e:
            logger.error(f"Classification error: {e}")
            # Fallback to "other" for safety
            return "other"
    
    def __call__(self, state: ConversationState) -> ConversationState:
        """
        LangGraph node function: classify the latest message.
        
        Args:
            state: Current conversation state
        
        Returns:
            Updated state with current_category set
        """
        # Get the last user message
        last_message = state["messages"][-1]
        user_text = last_message.content
        
        # Classify
        category = self.classify(user_text)
        
        # Update state
        state["current_category"] = category
        state["last_agent"] = "router"
        state["turn_count"] += 1
        
        logger.info(f"Router updated state: category={category}, turn={state['turn_count']}")
        
        return state
