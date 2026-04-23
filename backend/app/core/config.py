import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "Edu-Nexus"
    API_V1_STR: str = "/api/v1"

    # Paths
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    UPLOAD_DIR: str = os.path.join(BASE_DIR, "uploads_v2")

    # Neo4j — V2 uses port 7688
    NEO4J_URI: str = os.getenv("NEO4J_URI", "bolt://localhost:7688")
    NEO4J_USER: str = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD: str = os.getenv("NEO4J_PASSWORD", "password123")

    # Anthropic (Claude)
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")

    # Skill Velocity threshold — % increase that triggers automated audit
    VELOCITY_ALERT_THRESHOLD: float = float(os.getenv("VELOCITY_ALERT_THRESHOLD", "30.0"))

    # Redis — V2 uses port 6380
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6380/0")

    class Config:
        case_sensitive = True

settings = Settings()

# Validate critical settings on startup
if not settings.ANTHROPIC_API_KEY:
    raise ValueError("CRITICAL: ANTHROPIC_API_KEY is not set in .env file!")

# Ensure upload directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
