"""
Technical Agent: Handles technical support using RAG.

Design principle: Grounded responses using retrieved context only.
Never hallucinates - always references source documents.
"""
import logging

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate

from config import settings
from state import ConversationState
from retriever.retriever import get_retriever

logger = logging.getLogger(__name__)


class TechnicalAgent:
    """
    Technical support agent with RAG capabilities.
    
    Design notes:
    - Retrieves context before generating response
    - System prompt enforces context-only answers
    - Stores retrieved context in state for transparency
    """
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.openai_model,
            temperature=settings.temperature,
            openai_api_key=settings.openai_api_key
        )
        self.retriever = get_retriever()
        self.system_prompt = self._load_system_prompt()
    
    def _load_system_prompt(self) -> str:
        """Load technical agent system prompt from file."""
        prompt_path = "./prompts/technical_system_prompt.txt"
        try:
            with open(prompt_path, "r") as f:
                return f.read().strip()
        except FileNotFoundError:
            logger.error(f"Technical system prompt not found at {prompt_path}")
            return "You are a technical support specialist. Answer using only the provided context."
    
    def _build_prompt(self, user_question: str, context: str) -> ChatPromptTemplate:
        """
        Build prompt with context injection.
        
        Args:
            user_question: The user's technical question
            context: Retrieved documentation context
        
        Returns:
            Formatted prompt template
        """
        # Replace placeholders in system prompt
        formatted_system = self.system_prompt.replace("{context}", context)
        formatted_system = formatted_system.replace("{question}", user_question)
        
        return ChatPromptTemplate.from_messages([
            ("system", formatted_system),
            ("human", user_question)
        ])
    
    def answer_question(self, question: str) -> tuple[str, str]:
        """
        Generate answer using RAG.
        
        Args:
            question: User's technical question
        
        Returns:
            Tuple of (answer, retrieved_context)
        """
        logger.info(f"Technical agent answering: {question[:100]}...")
        
        # Step 1: Retrieve context
        context = self.retriever.get_context_for_query(question)
        logger.debug(f"Retrieved context length: {len(context)} chars")
        
        # Step 2: Generate answer
        prompt = self._build_prompt(question, context)
        messages = prompt.format_messages()
        
        response = self.llm.invoke(messages)
        answer = response.content
        
        logger.info(f"✓ Technical agent responded ({len(answer)} chars)")
        
        return answer, context
    
    def __call__(self, state: ConversationState) -> ConversationState:
        """
        LangGraph node function: generate technical support response.
        
        Args:
            state: Current conversation state
        
        Returns:
            Updated state with agent response added to messages
        """
        # Get the last user message
        last_message = state["messages"][-1]
        user_question = last_message.content
        
        # Generate answer with RAG
        answer, context = self.answer_question(user_question)
        
        # Update state
        state["messages"].append(AIMessage(content=answer))
        state["retrieved_context"] = context  # Store for audit/debugging
        state["last_agent"] = "technical"
        
        logger.info(f"Technical agent updated state (message count: {len(state['messages'])})")
        
        return state
