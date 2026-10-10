"""
Embedding service for generating text embeddings using Google GenAI (Gemini) or OpenAI.
Focused solely on vector embeddings for RAG retrieval.
"""

import logging
from typing import List
from ..core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class EmbeddingService:
    """Service for generating text embeddings using Gemini or OpenAI."""
    
    def __init__(self):
        """Initialize AI client for embeddings based on configuration."""
        self.provider = settings.ai_provider
        
        if self.provider == "gemini":
            from google import genai
            self.gemini_client = genai.Client(api_key=settings.gemini_api_key)
            self.embed_model = settings.gemini_embed_model
        elif self.provider == "openai":
            import openai
            self.openai_client = openai.OpenAI(api_key=settings.openai_api_key)
            self.embed_model = settings.openai_embed_model
        else:
            raise ValueError(f"Unsupported embedding provider: {self.provider}")
    
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors (768 dimensions for Gemini text-embedding-004)
        """
        try:
            if self.provider == "gemini":
                # Format texts as a list of lists for batch embedding
                batch_contents = [[text] for text in texts]
                response = self.gemini_client.models.embed_content(
                    model=self.embed_model,
                    contents=batch_contents,
                    config={"output_dimensionality": 1536}
                )
                embeddings = response.embeddings
                logger.info(f"Generated embeddings for {len(texts)} texts using Gemini")
                return [embedding.values for embedding in embeddings]
                
            elif self.provider == "openai":
                response = self.openai_client.embeddings.create(
                    model=self.embed_model,
                    input=texts
                )
                embeddings = [item.embedding for item in response.data]
                logger.info(f"Generated embeddings for {len(texts)} texts using OpenAI")
                return embeddings
                
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            raise
    
    async def embed_query(self, query: str) -> List[float]:
        """
        Generate embedding for a single query.
        
        Args:
            query: Query text to embed
            
        Returns:
            Embedding vector
        """
        embeddings = await self.embed_texts([query])
        return embeddings[0]


embedding_service = EmbeddingService()
