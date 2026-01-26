"""
Unit tests for LLM adapters.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.llm_adapter import (
    BaseLLMAdapter,
    OpenAIAdapter,
    DeepSeekAdapter,
    OllamaAdapter,
    get_llm_adapter
)


class TestBaseLLMAdapter:
    """Tests for BaseLLMAdapter."""
    
    def test_initialization(self):
        """Test adapter initialization."""
        adapter = OpenAIAdapter(model_name="gpt-4", temperature=0.8, api_key="test-key")
        assert adapter.model_name == "gpt-4"
        assert adapter.temperature == 0.8
        assert adapter.api_key == "test-key"
    
    def test_default_temperature(self):
        """Test default temperature value."""
        # Provide a test key to avoid initialization errors
        adapter = OpenAIAdapter(model_name="gpt-3.5-turbo", api_key="test-key")
        assert adapter.temperature == 0.7


@pytest.mark.asyncio
class TestOpenAIAdapter:
    """Tests for OpenAIAdapter."""
    
    async def test_generate_success(self):
        """Test successful response generation."""
        adapter = OpenAIAdapter(model_name="gpt-3.5-turbo", api_key="test-key")
        
        # Mock the OpenAI client
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "This is a test response."
        
        with patch.object(adapter.client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = mock_response
            
            messages = [{"role": "user", "content": "Hello"}]
            system_prompt = "You are a helpful assistant."
            
            result = await adapter.generate(messages, system_prompt)
            
            assert result == "This is a test response."
            mock_create.assert_called_once()
            
            # Verify the call arguments
            call_args = mock_create.call_args
            assert call_args.kwargs['model'] == "gpt-3.5-turbo"
            assert call_args.kwargs['temperature'] == 0.7
            assert len(call_args.kwargs['messages']) == 2  # system + user
    
    async def test_generate_empty_response(self):
        """Test handling of empty response."""
        adapter = OpenAIAdapter(model_name="gpt-3.5-turbo", api_key="test-key")
        
        # Mock empty response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = None
        
        with patch.object(adapter.client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = mock_response
            
            messages = [{"role": "user", "content": "Hello"}]
            system_prompt = "You are a helpful assistant."
            
            with pytest.raises(Exception, match="Failed to generate response from OpenAI"):
                await adapter.generate(messages, system_prompt)
    
    async def test_generate_api_error(self):
        """Test handling of API errors."""
        adapter = OpenAIAdapter(model_name="gpt-3.5-turbo", api_key="test-key")
        
        with patch.object(adapter.client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.side_effect = Exception("API Error")
            
            messages = [{"role": "user", "content": "Hello"}]
            system_prompt = "You are a helpful assistant."
            
            with pytest.raises(Exception, match="Failed to generate response from OpenAI"):
                await adapter.generate(messages, system_prompt)


@pytest.mark.asyncio
class TestDeepSeekAdapter:
    """Tests for DeepSeekAdapter."""
    
    async def test_generate_success(self):
        """Test successful response generation."""
        adapter = DeepSeekAdapter(model_name="deepseek-chat", api_key="test-key")
        
        # Mock the DeepSeek client (same interface as OpenAI)
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "DeepSeek response"
        
        with patch.object(adapter.client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = mock_response
            
            messages = [{"role": "user", "content": "Test"}]
            system_prompt = "You are DeepSeek."
            
            result = await adapter.generate(messages, system_prompt)
            
            assert result == "DeepSeek response"


@pytest.mark.asyncio
class TestOllamaAdapter:
    """Tests for OllamaAdapter."""
    
    async def test_generate_success(self):
        """Test successful response generation."""
        adapter = OllamaAdapter(model_name="llama3")
        
        # Mock httpx response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "message": {"content": "Ollama response"}
        }
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client_class.return_value = mock_client
            
            messages = [{"role": "user", "content": "Test"}]
            system_prompt = "You are Ollama."
            
            result = await adapter.generate(messages, system_prompt)
            
            assert result == "Ollama response"
    
    async def test_generate_empty_response(self):
        """Test handling of empty response from Ollama."""
        adapter = OllamaAdapter(model_name="llama3")
        
        # Mock empty response
        mock_response = MagicMock()
        mock_response.json.return_value = {"message": {}}
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client_class.return_value = mock_client
            
            messages = [{"role": "user", "content": "Test"}]
            system_prompt = "You are Ollama."
            
            with pytest.raises(Exception, match="Failed to generate response from Ollama"):
                await adapter.generate(messages, system_prompt)


class TestGetLLMAdapter:
    """Tests for get_llm_adapter factory function."""
    
    def test_get_openai_adapter(self):
        """Test getting OpenAI adapter."""
        adapter = get_llm_adapter("openai", "gpt-4", 0.8, api_key="test-key")
        assert isinstance(adapter, OpenAIAdapter)
        assert adapter.model_name == "gpt-4"
        assert adapter.temperature == 0.8
    
    def test_get_deepseek_adapter(self):
        """Test getting DeepSeek adapter."""
        adapter = get_llm_adapter("deepseek", "deepseek-chat", api_key="test-key")
        assert isinstance(adapter, DeepSeekAdapter)
        assert adapter.model_name == "deepseek-chat"
    
    def test_get_ollama_adapter(self):
        """Test getting Ollama adapter."""
        adapter = get_llm_adapter("ollama", "llama3")
        assert isinstance(adapter, OllamaAdapter)
        assert adapter.model_name == "llama3"
    
    def test_unsupported_provider(self):
        """Test error for unsupported provider."""
        with pytest.raises(ValueError, match="Unsupported provider"):
            get_llm_adapter("unsupported", "model")
    
    def test_case_insensitive_provider(self):
        """Test that provider name is case-insensitive."""
        adapter1 = get_llm_adapter("OpenAI", "gpt-4", api_key="test-key")
        adapter2 = get_llm_adapter("OPENAI", "gpt-4", api_key="test-key")
        assert isinstance(adapter1, OpenAIAdapter)
        assert isinstance(adapter2, OpenAIAdapter)
