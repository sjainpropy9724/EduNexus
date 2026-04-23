import os
from dotenv import load_dotenv
import anthropic

load_dotenv()

class ClaudeKeyManager:
    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("CRITICAL: ANTHROPIC_API_KEY not found in .env file!")
        
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = "claude-sonnet-4-5"
        print(f"✅ Claude API initialized (model: {self.model})")

    def get_client(self) -> anthropic.Anthropic:
        return self.client

    def get_model(self) -> str:
        return self.model

key_manager = ClaudeKeyManager()
