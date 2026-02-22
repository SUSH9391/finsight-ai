# Embeddings service using sentence-transformers (free, local)
# Will be fully implemented in Day 3

class EmbeddingService:
    def __init__(self):
        self.model = None  # Will load sentence-transformers model
    
    def load_model(self):
        """Load the embedding model — implemented in Day 3"""
        pass
    
    def embed_text(self, text: str):
        """Generate embeddings for text — implemented in Day 3"""
        pass
    
    def embed_batch(self, texts: list):
        """Generate embeddings for multiple texts — implemented in Day 3"""
        pass

embedding_service = EmbeddingService()