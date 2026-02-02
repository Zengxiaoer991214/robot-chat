"""
LLM Adapter Pattern for unified API calls to different providers.
"""
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import httpx
from openai import AsyncOpenAI
from google import genai
from app.core.config import settings

logger = logging.getLogger(__name__)


class BaseLLMAdapter(ABC):
    """Base class for LLM adapters."""
    
    def __init__(self, model_name: str, temperature: float = 0.7, api_key: Optional[str] = None):
        """
        Initialize the adapter.
        
        Args:
            model_name: Name of the model to use
            temperature: Temperature parameter for generation
            api_key: API key for the provider (if None, uses default from settings)
        """
        self.model_name = model_name
        self.temperature = temperature
        self.api_key = api_key
    
    @abstractmethod
    async def generate(self, messages: List[Dict[str, str]], system_prompt: str) -> str:
        """
        Generate a response from the LLM.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            system_prompt: System prompt to set the agent's personality
            
        Returns:
            Generated response text
            
        Raises:
            Exception: If generation fails
        """
        raise NotImplementedError


class OpenAIAdapter(BaseLLMAdapter):
    """Adapter for OpenAI API (GPT models)."""
    
    def __init__(self, model_name: str = "gpt-3.5-turbo", temperature: float = 0.7, api_key: Optional[str] = None):
        super().__init__(model_name, temperature, api_key)
        # Use provided API key or fall back to settings
        key = self.api_key or settings.openai_api_key
        if not key:
            logger.warning("No OpenAI API key provided")
            # For testing purposes only - should not be used in production
            if settings.debug:
                key = "dummy-key-for-testing"
            else:
                raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or provide api_key parameter.")
        self.client = AsyncOpenAI(api_key=key)
    
    async def generate(self, messages: List[Dict[str, str]], system_prompt: str) -> str:
        """
        Generate response using OpenAI API.
        
        Args:
            messages: Conversation history
            system_prompt: System prompt for the agent
            
        Returns:
            Generated response
            
        Raises:
            Exception: If API call fails
        """
        try:
            # Prepend system message
            full_messages = [{"role": "system", "content": system_prompt}] + messages
            
            logger.info(f"Calling OpenAI API with model {self.model_name}")
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=full_messages,
                temperature=self.temperature,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            if not content:
                raise ValueError("Empty response from OpenAI API")
                
            logger.info(f"OpenAI API response received: {len(content)} characters")
            return content.strip()
            
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise Exception(f"Failed to generate response from OpenAI: {str(e)}")


class DeepSeekAdapter(BaseLLMAdapter):
    """Adapter for DeepSeek API (compatible with OpenAI format)."""
    
    def __init__(self, model_name: str = "deepseek-chat", temperature: float = 0.7, api_key: Optional[str] = None):
        super().__init__(model_name, temperature, api_key)
        # DeepSeek uses OpenAI-compatible API
        key = self.api_key or settings.deepseek_api_key
        if not key:
            logger.warning("No DeepSeek API key provided")
            # For testing purposes only - should not be used in production
            if settings.debug:
                key = "dummy-key-for-testing"
            else:
                raise ValueError("DeepSeek API key is required. Set DEEPSEEK_API_KEY environment variable or provide api_key parameter.")
        self.client = AsyncOpenAI(
            api_key=key,
            base_url="https://api.deepseek.com"
        )
    
    async def generate(self, messages: List[Dict[str, str]], system_prompt: str) -> str:
        """
        Generate response using DeepSeek API.
        
        Args:
            messages: Conversation history
            system_prompt: System prompt for the agent
            
        Returns:
            Generated response
            
        Raises:
            Exception: If API call fails
        """
        try:
            # Prepend system message
            full_messages = [{"role": "system", "content": system_prompt}] + messages
            
            logger.info(f"Calling DeepSeek API with model {self.model_name}")
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=full_messages,
                temperature=self.temperature,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            if not content:
                raise ValueError("Empty response from DeepSeek API")
                
            logger.info(f"DeepSeek API response received: {len(content)} characters")
            return content.strip()
            
        except Exception as e:
            logger.error(f"DeepSeek API error: {str(e)}")
            raise Exception(f"Failed to generate response from DeepSeek: {str(e)}")


class ChatAnywhereAdapter(BaseLLMAdapter):
    """Adapter for ChatAnywhere API (Free OpenAI-compatible)."""
    
    def __init__(self, model_name: str = "gpt-3.5-turbo", temperature: float = 0.7, api_key: Optional[str] = None):
        super().__init__(model_name, temperature, api_key)
        # ChatAnywhere uses OpenAI-compatible API with a specific base URL
        key = self.api_key
        if not key:
            logger.warning("No ChatAnywhere API key provided")
            raise ValueError("ChatAnywhere API key is required. Provide api_key parameter.")
            
        self.client = AsyncOpenAI(
            api_key=key,
            base_url="https://api.chatanywhere.tech/v1"
        )
    
    async def generate(self, messages: List[Dict[str, str]], system_prompt: str) -> str:
        """
        Generate response using ChatAnywhere API.
        """
        try:
            # Prepend system message
            full_messages = [{"role": "system", "content": system_prompt}] + messages
            
            logger.info(f"Calling ChatAnywhere API with model {self.model_name}")
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=full_messages,
                temperature=self.temperature,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            if not content:
                raise ValueError("Empty response from ChatAnywhere API")
                
            logger.info(f"ChatAnywhere API response received: {len(content)} characters")
            return content.strip()
            
        except Exception as e:
            logger.error(f"ChatAnywhere API error: {str(e)}")
            raise Exception(f"Failed to generate response from ChatAnywhere: {str(e)}")


class GoogleAdapter(BaseLLMAdapter):
    """Adapter for Google Gemini API."""
    
    def __init__(self, model_name: str = "gemini-2.0-flash-exp", temperature: float = 0.7, api_key: Optional[str] = None):
        super().__init__(model_name, temperature, api_key)
        key = self.api_key
        if not key:
             logger.warning("No Google API key provided")
             raise ValueError("Google API key is required. Provide api_key parameter.")
        
        # Initialize Google GenAI client
        self.client = genai.Client(api_key=key)

    async def generate(self, messages: List[Dict[str, str]], system_prompt: str) -> str:
        """
        Generate response using Google Gemini API (v1 SDK).
        """
        try:
            logger.info(f"Calling Google Gemini API with model {self.model_name}")
            
            # Construct prompt from history
            # We combine system prompt and messages into a single string context for simplicity with generate_content
            # Alternatively, we could use chat features if we mapped roles correctly.
            # But based on user request "Explain how AI works in a few words" example, they used generate_content.
            
            prompt_parts = []
            if system_prompt:
                prompt_parts.append(f"System: {system_prompt}")
            
            for msg in messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                prompt_parts.append(f"{role}: {content}")
            
            prompt_parts.append("assistant: ")
            full_prompt = "\n".join(prompt_parts)
            
            # Run synchronous generate_content in thread pool
            # User example: response = client.models.generate_content(model="...", contents="...")
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model_name,
                contents=full_prompt
            )
            
            if not response.text:
                 raise ValueError("Empty response from Google API")

            logger.info(f"Google API response received: {len(response.text)} characters")
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Google API error: {str(e)}")
            raise Exception(f"Failed to generate response from Google: {str(e)}")


class OllamaAdapter(BaseLLMAdapter):
    """Adapter for local Ollama models."""
    
    def __init__(self, model_name: str = "llama3", temperature: float = 0.7, api_key: Optional[str] = None, base_url: str = "http://localhost:11434"):
        super().__init__(model_name, temperature, api_key)
        self.base_url = base_url
    
    async def generate(self, messages: List[Dict[str, str]], system_prompt: str) -> str:
        """
        Generate response using Ollama local API.
        
        Args:
            messages: Conversation history
            system_prompt: System prompt for the agent
            
        Returns:
            Generated response
            
        Raises:
            Exception: If API call fails
        """
        try:
            # Prepend system message
            full_messages = [{"role": "system", "content": system_prompt}] + messages
            
            logger.info(f"Calling Ollama API with model {self.model_name}")
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/chat",
                    json={
                        "model": self.model_name,
                        "messages": full_messages,
                        "stream": False,
                        "options": {"temperature": self.temperature}
                    }
                )
                response.raise_for_status()
                data = response.json()
                
                content = data.get("message", {}).get("content", "")
                if not content:
                    raise ValueError("Empty response from Ollama API")
                    
                logger.info(f"Ollama API response received: {len(content)} characters")
                return content.strip()
                
        except Exception as e:
            logger.error(f"Ollama API error: {str(e)}")
            raise Exception(f"Failed to generate response from Ollama: {str(e)}")


def get_llm_adapter(provider: str, model_name: str, temperature: float = 0.7, api_key: Optional[str] = None) -> BaseLLMAdapter:
    """
    Factory function to get the appropriate LLM adapter.
    
    Args:
        provider: Provider name (openai, deepseek, ollama, google)
        model_name: Model name
        temperature: Temperature parameter
        api_key: Optional API key
        
    Returns:
        Appropriate LLM adapter instance
        
    Raises:
        ValueError: If provider is not supported
    """
    provider = provider.lower()
    
    if provider == "openai":
        return OpenAIAdapter(model_name, temperature, api_key)
    elif provider == "deepseek":
        return DeepSeekAdapter(model_name, temperature, api_key)
    elif provider == "ollama":
        return OllamaAdapter(model_name, temperature, api_key)
    elif provider == "google":
        return GoogleAdapter(model_name, temperature, api_key)
    elif provider == "chatanywhere":
        return ChatAnywhereAdapter(model_name, temperature, api_key)
    elif provider == "dashscope" or provider == "aliyun":
        return DashScopeAdapter(model_name, temperature, api_key)
    else:
        raise ValueError(f"Unsupported provider: {provider}")
