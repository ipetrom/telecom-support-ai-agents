"""
Configuration management using Pydantic Settings.
Centralizes all environment variables and app configuration.
"""
from pydantic_settings import BaseSettings
from typing import Literal


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # OpenAI Configuration
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"
    temperature: float = 0.0
    
    # Vector Store Configuration
    vector_store_type: Literal["faiss", "opensearch"] = "faiss"
    vector_store_path: str = "./data/vectorstore"
    opensearch_url: str = "http://localhost:9200"
    
    # Application Configuration
    log_level: str = "INFO"
    max_history_length: int = 10
    
    # Retriever Configuration
    retrieval_k: int = 3  # Number of documents to retrieve
    chunk_size: int = 1000
    chunk_overlap: int = 200
    
    # Mock Data (for development)
    mock_user_id: str = "user_12345"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields in .env


# Singleton instance
settings = Settings()
