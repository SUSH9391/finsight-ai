# Ollama LLM wrapper service
# Will be fully implemented in Day 3

class LLMService:
    def __init__(self):
        self.base_url = "http://localhost:11434"
        self.model = "mistral"
    
    def generate(self, prompt: str) -> str:
        """Generate response from local LLM — implemented in Day 3"""
        raise NotImplementedError("LLM generate() will be implemented in Day 3")    
    def stream(self, prompt: str):
        """Stream response from local LLM — implemented in Day 3"""
        pass

llm_service = LLMService()