"""
Configuration management for Shakespeare Translator.
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load .env file
ENV_FILE = Path(__file__).parent / ".env"
if ENV_FILE.exists():
    load_dotenv(ENV_FILE)


class Settings(BaseSettings):
    """Application settings from environment."""
    
    # API Configuration
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    
    # Server Configuration
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Model Configuration
    model: str = os.getenv("MODEL", "claude-haiku-4-5-20251001")
    
    # Rate Limiting
    rate_limit_per_minute: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "30"))
    
    # CORS
    cors_origins: list = [
        "http://localhost:3000",
        "http://localhost:8000",
        "https://yourdomain.com"
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    def validate(self) -> bool:
        """Validate critical configuration."""
        if not self.anthropic_api_key:
            print("❌ ERROR: ANTHROPIC_API_KEY not set")
            return False
        
        if not self.anthropic_api_key.startswith("sk-ant"):
            print("⚠️  WARNING: ANTHROPIC_API_KEY looks invalid")
        
        return True
    
    def summary(self):
        """Print configuration summary."""
        print("=" * 60)
        print("  SHAKESPEARE TRANSLATOR — Configuration")
        print("=" * 60)
        print(f"\n🔑 API Key:      {self.anthropic_api_key[:20]}...")
        print(f"🤖 Model:        {self.model}")
        print(f"🌐 Host:         {self.host}:{self.port}")
        print(f"🚦 Rate Limit:   {self.rate_limit_per_minute} req/min")
        print(f"🔄 Debug Mode:   {'Enabled' if self.debug else 'Disabled'}")
        print()


# Global settings instance
settings = Settings()
