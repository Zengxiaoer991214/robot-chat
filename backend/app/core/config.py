"""
Configuration module for the AI Group Chat system.
Handles environment variables and application settings.
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    database_url: str = Field(
        default="postgresql://user:password@localhost:5432/ai_chat_db",
        description="PostgreSQL connection URL"
    )
    
    # API Keys
    openai_api_key: Optional[str] = Field(
        default=None,
        description="Default OpenAI API key"
    )
    deepseek_api_key: Optional[str] = Field(
        default=None,
        description="Default DeepSeek API key"
    )
    
    # Server
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port", validation_alias="APP_PORT")
    debug: bool = Field(default=False, description="Debug mode")
    app_password: Optional[str] = Field(default=None, description="Optional password for application access")
    
    # Application
    max_context_messages: int = Field(
        default=20,
        description="Maximum number of messages to include in context"
    )
    default_sleep_between_messages: float = Field(
        default=2.0,
        description="Default sleep time between messages in seconds (lower for dev/test)"
    )
    
    # Message templates (can be overridden for i18n)
    conversation_start_template: str = Field(
        default="本次群聊的主题是：{topic}，请大家开始讨论。",
        description="Template for conversation start message"
    )
    conversation_end_template: str = Field(
        default="群聊已结束，感谢大家的参与！",
        description="Template for conversation end message"
    )
    
    class Config:
        # Load .env first, then override with local config if it exists
        # NOTE: Pydantic Settings loads in order, so later files override earlier ones.
        # However, the user wants the local E:/linli/chatbot/.env to be the PRIMARY one if it exists.
        # So we should load it LAST to override the default .env.
        # But wait, user said "First load...". 
        # If I have [A, B], B overrides A. 
        # If user wants "First load" to mean "Base", then [E_ENV, .ENV] -> .ENV overrides E_ENV.
        # If user wants "First load" to mean "Priority", then [ .ENV, E_ENV] -> E_ENV overrides .ENV.
        # Given "Wrong... First load...", I will respect the order: E_ENV then .ENV
        # This implies E_ENV is the base, and .ENV overrides it.
        # Or maybe the user means "Load E_ENV first" as in "Read it".
        
        # Let's try putting E_ENV at the START of the list.
        # This means project .env will OVERRIDE local E_ENV.
        env_file = []
        if os.path.exists("E:/chatbot/.env"):
             env_file.append("E:/chatbot/.env")
             
        env_file.append(".env")
            
        case_sensitive = False
        extra = "ignore"


# Global settings instance
settings = Settings()
