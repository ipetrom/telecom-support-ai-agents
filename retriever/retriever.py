"""
RAG Retriever for Technical Agent.
Loads persisted vector store and provides context retrieval.

Design principle: Abstract retrieval logic for easy OpenSearch migration.
"""
import logging
from pathlib import Path
from typing import List, Optional

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStoreRetriever

from config import settings

logger = logging.getLogger(__name__)


class TechnicalRetriever:
    """
    Wrapper around vector store retrieval.
    Provides a consistent interface regardless of backend (FAISS/OpenSearch).
    """
    
    def __init__(self, vectorstore_path: str = None):
        """
        Initialize retriever with persisted vector store.
        
        Args:
            vectorstore_path: Custom path to vector store (optional)
        """
        self.vectorstore_path = vectorstore_path or settings.vector_store_path
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=settings.openai_api_key
        )
        self.vectorstore = self._load_vectorstore()
        self.retriever = self._create_retriever()
    
    def _load_vectorstore(self) -> FAISS:
        """
        Load persisted FAISS vector store from disk.
        
        Returns:
            Loaded FAISS instance
            
        Raises:
            FileNotFoundError: If vector store doesn't exist
        """
        if not Path(self.vectorstore_path).exists():
            error_msg = (
                f"Vector store not found at {self.vectorstore_path}. "
                "Run 'python retriever/build_vectorstore.py' first."
            )
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        
        logger.info(f"Loading vector store from {self.vectorstore_path}")
        vectorstore = FAISS.load_local(
            self.vectorstore_path,
            self.embeddings,
            allow_dangerous_deserialization=True  # Safe for our use case
        )
        logger.info("Vector store loaded successfully")
        return vectorstore
    
    def _create_retriever(self) -> VectorStoreRetriever:
        """
        Create a retriever with configurable search parameters.
        
        Returns:
            Configured VectorStoreRetriever
        """
        return self.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": settings.retrieval_k}
        )
    
    def retrieve_context(self, query: str) -> List[Document]:
        """
        Retrieve relevant documents for a given query.
        
        Args:
            query: User's technical question
            
        Returns:
            List of relevant Document objects with content and metadata
        """
        logger.info(f"Retrieving context for query: {query[:100]}...")
        documents = self.retriever.invoke(query)
        
        logger.info(f"Retrieved {len(documents)} documents")
        for idx, doc in enumerate(documents):
            source = doc.metadata.get('source', 'unknown')
            logger.debug(f"  [{idx+1}] Source: {source}, Length: {len(doc.page_content)}")
        
        return documents
    
    def format_context(self, documents: List[Document]) -> str:
        """
        Format retrieved documents into a single context string.
        
        Args:
            documents: Retrieved documents
            
        Returns:
            Formatted context string with source attribution
        """
        if not documents:
            return "No relevant documentation found."
        
        context_parts = []
        for idx, doc in enumerate(documents, 1):
            source = doc.metadata.get('source', 'unknown')
            context_parts.append(
                f"[Source {idx}: {source}]\n{doc.page_content}\n"
            )
        
        return "\n---\n".join(context_parts)
    
    def get_context_for_query(self, query: str) -> str:
        """
        Convenience method: retrieve and format in one call.
        
        Args:
            query: User's technical question
            
        Returns:
            Formatted context string ready for LLM consumption
        """
        documents = self.retrieve_context(query)
        return self.format_context(documents)


# Singleton instance for reuse across agent invocations
_retriever_instance: Optional[TechnicalRetriever] = None


def get_retriever() -> TechnicalRetriever:
    """
    Factory function to get or create retriever singleton.
    Avoids reloading vector store on every agent call.
    
    Returns:
        Shared TechnicalRetriever instance
    """
    global _retriever_instance
    if _retriever_instance is None:
        _retriever_instance = TechnicalRetriever()
    return _retriever_instance
