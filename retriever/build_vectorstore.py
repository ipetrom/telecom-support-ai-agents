"""
Vector Store Initialization.
Builds FAISS index from technical documentation.

Migration note: Replace FAISS with OpenSearchVectorSearch for production.
Keep the same interface (from_documents) for seamless transition.
"""
import logging
from pathlib import Path
from typing import List

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from config import settings

logger = logging.getLogger(__name__)


class VectorStoreBuilder:
    """Handles vector store creation and persistence."""
    
    def __init__(self, docs_path: str = "./data/docs"):
        self.docs_path = Path(docs_path)
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=settings.openai_api_key
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def load_documents(self) -> List[Document]:
        """
        Load all markdown documents from the docs directory.
        
        Returns:
            List of Document objects with content and metadata
        """
        logger.info(f"Loading documents from {self.docs_path}")
        
        loader = DirectoryLoader(
            str(self.docs_path),
            glob="**/*.md",
            loader_cls=TextLoader,
            show_progress=True
        )
        
        documents = loader.load()
        logger.info(f"Loaded {len(documents)} documents")
        
        # Add source metadata for transparency
        for doc in documents:
            doc.metadata["source"] = Path(doc.metadata.get("source", "")).name
        
        return documents
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into chunks for better retrieval granularity.
        
        Args:
            documents: Raw documents from loader
            
        Returns:
            List of chunked documents
        """
        logger.info("Splitting documents into chunks")
        chunks = self.text_splitter.split_documents(documents)
        logger.info(f"Created {len(chunks)} chunks")
        return chunks
    
    def build_vectorstore(self, chunks: List[Document]) -> FAISS:
        """
        Create FAISS vector store from document chunks.
        
        Args:
            chunks: Document chunks to embed
            
        Returns:
            FAISS vector store instance
        """
        logger.info("Building FAISS vector store")
        vectorstore = FAISS.from_documents(
            documents=chunks,
            embedding=self.embeddings
        )
        logger.info("Vector store built successfully")
        return vectorstore
    
    def save_vectorstore(self, vectorstore: FAISS, path: str = None):
        """
        Persist vector store to disk.
        
        Args:
            vectorstore: FAISS instance to save
            path: Custom save path (optional)
        """
        save_path = path or settings.vector_store_path
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Saving vector store to {save_path}")
        vectorstore.save_local(save_path)
        logger.info("Vector store saved successfully")
    
    def build_and_save(self):
        """
        Complete pipeline: load, chunk, build, and persist vector store.
        """
        documents = self.load_documents()
        chunks = self.split_documents(documents)
        vectorstore = self.build_vectorstore(chunks)
        self.save_vectorstore(vectorstore)
        
        logger.info("✅ Vector store initialization complete")


def main():
    """CLI entry point for building the vector store."""
    logging.basicConfig(
        level=settings.log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    builder = VectorStoreBuilder()
    builder.build_and_save()


if __name__ == "__main__":
    main()
