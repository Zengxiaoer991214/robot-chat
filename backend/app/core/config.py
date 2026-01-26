"""
Configuration module for the AI Group Chat system.
Handles environment variables and application settings.
"""
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
    port: int = Field(default=8000, description="Server port")
    debug: bool = Field(default=False, description="Debug mode")
    
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
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
