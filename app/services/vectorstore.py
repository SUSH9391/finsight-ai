# ChromaDB vector store service
# Will be fully implemented in Day 3

class VectorStoreService:
    def __init__(self):
        self.client = None
        self.collection = None
    
    def initialize(self):
        """Initialize ChromaDB — implemented in Day 3"""
        pass
    
    def add_transactions(self, transactions: list):
        """Store transaction embeddings — implemented in Day 3"""
        pass
    
    def search(self, query: str, top_k: int = 5):
        """Semantic search over transactions — implemented in Day 3"""
        pass

vector_store = VectorStoreService()