"""
Embedding Configuration System for Symmetra

This module provides a unified interface for different embedding backends:
- Cloud embeddings (OpenAI, Cohere, etc.) - Recommended for production
- Local embeddings (SentenceTransformers) - For development/offline use
"""

import os
import logging
from typing import List, Dict, Any, Optional, Union
from enum import Enum
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class EmbeddingBackend(Enum):
    """Available embedding backends"""
    OPENAI = "openai"
    COHERE = "cohere"
    LOCAL = "local"
    AUTO = "auto"  # Automatically choose best available

class EmbeddingProvider:
    """Base class for embedding providers"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding for text"""
        raise NotImplementedError
    
    def generate_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        embeddings = []
        for text in texts:
            embedding = self.generate_embedding(text)
            if embedding:
                embeddings.append(embedding)
            else:
                # Use zero vector as fallback
                embeddings.append([0.0] * self.get_dimensions())
        return embeddings
    
    def is_available(self) -> bool:
        """Check if this provider is available"""
        raise NotImplementedError
    
    def get_dimensions(self) -> int:
        """Get embedding dimensions"""
        return 384  # Default to 384 for compatibility

class OpenAIEmbeddingProvider(EmbeddingProvider):
    """OpenAI cloud embedding provider"""
    
    def __init__(self):
        super().__init__()
        self._client = None
        load_dotenv()
    
    def _get_client(self):
        """Lazy initialization of OpenAI client"""
        if self._client is None:
            try:
                from openai import OpenAI
                api_key = os.getenv('OPENAI_API_KEY')
                if not api_key:
                    self.logger.warning("OPENAI_API_KEY not found")
                    return None
                self._client = OpenAI(api_key=api_key)
            except Exception as e:
                self.logger.error(f"Failed to initialize OpenAI client: {e}")
                return None
        return self._client
    
    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding using OpenAI API"""
        client = self._get_client()
        if not client:
            return None
        
        try:
            cleaned_text = text.replace("\n", " ").strip()
            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=[cleaned_text],
                dimensions=384
            )
            return response.data[0].embedding
        except Exception as e:
            self.logger.error(f"OpenAI embedding failed: {e}")
            return None
    
    def generate_batch_embeddings(self, texts: List[str], batch_size: int = 100) -> List[List[float]]:
        """Generate embeddings in batches for efficiency"""
        client = self._get_client()
        if not client:
            return super().generate_batch_embeddings(texts)
        
        embeddings = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            cleaned_batch = [text.replace("\n", " ").strip() for text in batch]
            
            try:
                response = client.embeddings.create(
                    model="text-embedding-3-small",
                    input=cleaned_batch,
                    dimensions=384
                )
                batch_embeddings = [item.embedding for item in response.data]
                embeddings.extend(batch_embeddings)
            except Exception as e:
                self.logger.error(f"Batch embedding failed: {e}")
                # Fall back to individual processing
                for text in batch:
                    embedding = self.generate_embedding(text)
                    embeddings.append(embedding or [0.0] * 384)
        
        return embeddings
    
    def is_available(self) -> bool:
        """Check if OpenAI API is available"""
        return self._get_client() is not None

class CohereEmbeddingProvider(EmbeddingProvider):
    """Cohere cloud embedding provider"""
    
    def __init__(self):
        super().__init__()
        self._client = None
        load_dotenv()
    
    def _get_client(self):
        """Lazy initialization of Cohere client"""
        if self._client is None:
            try:
                import cohere
                api_key = os.getenv('COHERE_API_KEY')
                if not api_key:
                    self.logger.warning("COHERE_API_KEY not found")
                    return None
                self._client = cohere.Client(api_key)
            except Exception as e:
                self.logger.error(f"Failed to initialize Cohere client: {e}")
                return None
        return self._client
    
    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding using Cohere API"""
        client = self._get_client()
        if not client:
            return None
        
        try:
            response = client.embed(
                texts=[text],
                model="embed-english-light-v3.0",  # 384 dimensions
                input_type="search_document"
            )
            return response.embeddings[0]
        except Exception as e:
            self.logger.error(f"Cohere embedding failed: {e}")
            return None
    
    def is_available(self) -> bool:
        """Check if Cohere API is available"""
        return self._get_client() is not None

class LocalEmbeddingProvider(EmbeddingProvider):
    """Local SentenceTransformers embedding provider"""
    
    def __init__(self):
        super().__init__()
        self._model = None
        load_dotenv()
    
    def _get_model(self):
        """Lazy initialization of local model"""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                model_name = os.getenv('SYMMETRA_EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
                self._model = SentenceTransformer(model_name)
                self.logger.info(f"Loaded local embedding model: {model_name}")
            except Exception as e:
                self.logger.error(f"Failed to load local model: {e}")
                return None
        return self._model
    
    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding using local model"""
        model = self._get_model()
        if not model:
            return None
        
        try:
            embedding = model.encode(text)
            return embedding.tolist()
        except Exception as e:
            self.logger.error(f"Local embedding failed: {e}")
            return None
    
    def is_available(self) -> bool:
        """Check if local model is available"""
        return self._get_model() is not None

class EmbeddingManager:
    """Central manager for embedding operations"""
    
    def __init__(self, backend: Union[EmbeddingBackend, str] = EmbeddingBackend.AUTO):
        """
        Initialize embedding manager
        
        Args:
            backend: Preferred embedding backend (auto-detected if not specified)
        """
        self.logger = logging.getLogger(__name__)
        
        if isinstance(backend, str):
            backend = EmbeddingBackend(backend)
        
        self.preferred_backend = backend
        self._provider = None
        self._initialize_provider()
    
    def _initialize_provider(self):
        """Initialize the embedding provider based on configuration"""
        if self.preferred_backend == EmbeddingBackend.AUTO:
            # Auto-detect best available provider
            providers_to_try = [
                (EmbeddingBackend.OPENAI, OpenAIEmbeddingProvider),
                (EmbeddingBackend.COHERE, CohereEmbeddingProvider),
                (EmbeddingBackend.LOCAL, LocalEmbeddingProvider)
            ]
            
            for backend_type, provider_class in providers_to_try:
                provider = provider_class()
                if provider.is_available():
                    self._provider = provider
                    self.logger.info(f"Auto-selected {backend_type.value} embedding provider")
                    break
            
            if not self._provider:
                self.logger.error("No embedding providers available")
                
        else:
            # Use specific provider
            provider_map = {
                EmbeddingBackend.OPENAI: OpenAIEmbeddingProvider,
                EmbeddingBackend.COHERE: CohereEmbeddingProvider,
                EmbeddingBackend.LOCAL: LocalEmbeddingProvider
            }
            
            provider_class = provider_map.get(self.preferred_backend)
            if provider_class:
                self._provider = provider_class()
                if self._provider.is_available():
                    self.logger.info(f"Using {self.preferred_backend.value} embedding provider")
                else:
                    self.logger.error(f"{self.preferred_backend.value} provider not available")
                    self._provider = None
    
    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding for text"""
        if not self._provider:
            self.logger.error("No embedding provider available")
            return None
        
        return self._provider.generate_embedding(text)
    
    def generate_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        if not self._provider:
            self.logger.error("No embedding provider available")
            return [[0.0] * 384 for _ in texts]  # Return zero vectors as fallback
        
        return self._provider.generate_batch_embeddings(texts)
    
    def is_available(self) -> bool:
        """Check if embedding generation is available"""
        return self._provider is not None and self._provider.is_available()
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about the current provider"""
        if not self._provider:
            return {"status": "unavailable", "provider": None}
        
        provider_name = self._provider.__class__.__name__.replace("EmbeddingProvider", "")
        return {
            "status": "available" if self._provider.is_available() else "unavailable",
            "provider": provider_name.lower(),
            "dimensions": self._provider.get_dimensions(),
            "preferred_backend": self.preferred_backend.value
        }

# Global embedding manager instance
def get_embedding_manager() -> EmbeddingManager:
    """Get the global embedding manager instance"""
    if not hasattr(get_embedding_manager, "_instance"):
        backend = os.getenv('SYMMETRA_EMBEDDING_BACKEND', 'auto')
        get_embedding_manager._instance = EmbeddingManager(backend)
    return get_embedding_manager._instance

# Convenience functions
def generate_embedding(text: str) -> Optional[List[float]]:
    """Generate embedding using the configured provider"""
    return get_embedding_manager().generate_embedding(text)

def generate_batch_embeddings(texts: List[str]) -> List[List[float]]:
    """Generate embeddings for multiple texts"""
    return get_embedding_manager().generate_batch_embeddings(texts)