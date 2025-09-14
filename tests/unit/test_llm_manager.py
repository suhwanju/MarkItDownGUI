"""
Unit tests for LLMManager
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json
import asyncio
from datetime import datetime

from markitdown_gui.core.llm_manager import LLMManager, LLMProvider, OCRResult, TokenUsage
from markitdown_gui.core.exceptions import LLMError, LLMConfigurationError, LLMAuthenticationError, LLMRateLimitError


class TestLLMManager:
    """Test suite for LLMManager"""
    
    def test_initialization(self, config_manager):
        """Test LLMManager initialization"""
        llm_manager = LLMManager(config_manager)
        
        assert llm_manager is not None
        assert llm_manager.config_manager == config_manager
        assert llm_manager.current_provider == LLMProvider.OPENAI
        assert llm_manager.api_client is None
        assert llm_manager.usage_history == []
    
    def test_supported_providers(self, config_manager):
        """Test supported LLM providers"""
        llm_manager = LLMManager(config_manager)
        
        providers = llm_manager.get_supported_providers()
        
        assert LLMProvider.OPENAI in providers
        assert LLMProvider.ANTHROPIC in providers
        assert LLMProvider.OLLAMA in providers
    
    @patch('keyring.get_password')
    @patch('keyring.set_password')
    def test_api_key_management(self, mock_set, mock_get, config_manager):
        """Test secure API key storage and retrieval"""
        llm_manager = LLMManager(config_manager)
        
        # Test setting API key
        test_key = "sk-test123456789"
        llm_manager.set_api_key(LLMProvider.OPENAI, test_key)
        
        mock_set.assert_called_with("MarkItDown-GUI", "openai_api_key", test_key)
        
        # Test getting API key
        mock_get.return_value = test_key
        retrieved_key = llm_manager.get_api_key(LLMProvider.OPENAI)
        
        assert retrieved_key == test_key
        mock_get.assert_called_with("MarkItDown-GUI", "openai_api_key")
    
    @patch('keyring.get_password')
    def test_api_key_not_found(self, mock_get, config_manager):
        """Test handling when API key is not found"""
        mock_get.return_value = None
        
        llm_manager = LLMManager(config_manager)
        key = llm_manager.get_api_key(LLMProvider.OPENAI)
        
        assert key is None
    
    @patch('keyring.get_password')
    def test_provider_configuration(self, mock_get, config_manager):
        """Test provider configuration"""
        mock_get.return_value = "sk-test123456789"
        
        llm_manager = LLMManager(config_manager)
        
        # Configure OpenAI
        success = llm_manager.configure_provider(
            LLMProvider.OPENAI,
            model="gpt-4o",
            api_base="https://api.openai.com/v1",
            max_tokens=4096,
            temperature=0.7
        )
        
        assert success == True
        assert llm_manager.current_provider == LLMProvider.OPENAI
        
        config = llm_manager.get_provider_config(LLMProvider.OPENAI)
        assert config['model'] == "gpt-4o"
        assert config['max_tokens'] == 4096
        assert config['temperature'] == 0.7
    
    def test_provider_configuration_without_api_key(self, config_manager):
        """Test provider configuration failure without API key"""
        llm_manager = LLMManager(config_manager)
        
        with patch('keyring.get_password', return_value=None):
            with pytest.raises(LLMConfigurationError):
                llm_manager.configure_provider(LLMProvider.OPENAI)
    
    @patch('aiohttp.ClientSession.post')
    @patch('keyring.get_password')
    async def test_text_generation_success(self, mock_get, mock_post, config_manager):
        """Test successful text generation"""
        mock_get.return_value = "sk-test123456789"
        
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = asyncio.coroutine(lambda: {
            "choices": [{
                "message": {
                    "content": "Generated text response"
                }
            }],
            "usage": {
                "total_tokens": 150,
                "prompt_tokens": 50,
                "completion_tokens": 100
            }
        })
        mock_post.return_value.__aenter__.return_value = mock_response
        
        llm_manager = LLMManager(config_manager)
        await llm_manager.configure_provider(LLMProvider.OPENAI)
        
        # Generate text
        result = await llm_manager.generate_text("Test prompt")
        
        assert result is not None
        assert "Generated text response" in result
        
        # Check usage tracking
        assert len(llm_manager.usage_history) == 1
        usage = llm_manager.usage_history[0]
        assert usage['total_tokens'] == 150
        assert usage['provider'] == LLMProvider.OPENAI.value
    
    @patch('aiohttp.ClientSession.post')
    @patch('keyring.get_password')
    async def test_ocr_processing_success(self, mock_get, mock_post, config_manager, temp_dir):
        """Test successful OCR processing"""
        mock_get.return_value = "sk-test123456789"
        
        # Create test image
        image_file = temp_dir / "test_image.png"
        image_file.write_bytes(b"fake image data")
        
        # Mock successful OCR API response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = asyncio.coroutine(lambda: {
            "choices": [{
                "message": {
                    "content": "Extracted text from image"
                }
            }],
            "usage": {
                "total_tokens": 200,
                "prompt_tokens": 100,
                "completion_tokens": 100
            }
        })
        mock_post.return_value.__aenter__.return_value = mock_response
        
        llm_manager = LLMManager(config_manager)
        await llm_manager.configure_provider(LLMProvider.OPENAI)
        
        # Process OCR
        result = await llm_manager.process_ocr(str(image_file))
        
        assert isinstance(result, OCRResult)
        assert result.success == True
        assert "Extracted text from image" in result.text
        assert result.confidence > 0
        assert result.processing_time > 0
    
    @patch('aiohttp.ClientSession.post')
    @patch('keyring.get_password')
    async def test_api_error_handling(self, mock_get, mock_post, config_manager):
        """Test API error handling"""
        mock_get.return_value = "sk-test123456789"
        
        # Test authentication error
        mock_response = MagicMock()
        mock_response.status = 401
        mock_response.json = asyncio.coroutine(lambda: {
            "error": {"message": "Invalid API key"}
        })
        mock_post.return_value.__aenter__.return_value = mock_response
        
        llm_manager = LLMManager(config_manager)
        await llm_manager.configure_provider(LLMProvider.OPENAI)
        
        with pytest.raises(LLMAuthenticationError):
            await llm_manager.generate_text("Test prompt")
    
    @patch('aiohttp.ClientSession.post')
    @patch('keyring.get_password')
    async def test_rate_limit_handling(self, mock_get, mock_post, config_manager):
        """Test rate limit error handling"""
        mock_get.return_value = "sk-test123456789"
        
        # Test rate limit error
        mock_response = MagicMock()
        mock_response.status = 429
        mock_response.json = asyncio.coroutine(lambda: {
            "error": {"message": "Rate limit exceeded"}
        })
        mock_post.return_value.__aenter__.return_value = mock_response
        
        llm_manager = LLMManager(config_manager)
        await llm_manager.configure_provider(LLMProvider.OPENAI)
        
        with pytest.raises(LLMRateLimitError):
            await llm_manager.generate_text("Test prompt")
    
    def test_token_usage_tracking(self, config_manager):
        """Test token usage tracking and statistics"""
        llm_manager = LLMManager(config_manager)
        
        # Add some mock usage data
        llm_manager.usage_history = [
            {
                'timestamp': datetime.now().isoformat(),
                'provider': 'openai',
                'model': 'gpt-4o',
                'total_tokens': 100,
                'prompt_tokens': 50,
                'completion_tokens': 50,
                'estimated_cost': 0.01
            },
            {
                'timestamp': datetime.now().isoformat(),
                'provider': 'openai',
                'model': 'gpt-4o',
                'total_tokens': 200,
                'prompt_tokens': 100,
                'completion_tokens': 100,
                'estimated_cost': 0.02
            }
        ]
        
        # Get usage statistics
        stats = llm_manager.get_usage_stats()
        
        assert stats['total_requests'] == 2
        assert stats['total_tokens'] == 300
        assert stats['total_cost'] == 0.03
        assert stats['average_tokens'] == 150
        
        # Get usage by provider
        provider_stats = llm_manager.get_usage_by_provider()
        assert 'openai' in provider_stats
        assert provider_stats['openai']['requests'] == 2
        assert provider_stats['openai']['tokens'] == 300
    
    def test_cost_estimation(self, config_manager):
        """Test cost estimation for different providers and models"""
        llm_manager = LLMManager(config_manager)
        
        # Test OpenAI GPT-4 cost estimation
        cost = llm_manager.estimate_cost(
            LLMProvider.OPENAI,
            "gpt-4o",
            prompt_tokens=1000,
            completion_tokens=500
        )
        
        assert cost > 0
        assert isinstance(cost, float)
        
        # Test different model
        cost_3_5 = llm_manager.estimate_cost(
            LLMProvider.OPENAI,
            "gpt-3.5-turbo",
            prompt_tokens=1000,
            completion_tokens=500
        )
        
        # GPT-4 should be more expensive than GPT-3.5
        assert cost > cost_3_5
    
    def test_usage_export_import(self, config_manager, temp_dir):
        """Test exporting and importing usage data"""
        llm_manager = LLMManager(config_manager)
        
        # Add mock usage data
        llm_manager.usage_history = [
            {
                'timestamp': datetime.now().isoformat(),
                'provider': 'openai',
                'total_tokens': 100,
                'estimated_cost': 0.01
            }
        ]
        
        # Export usage data
        export_file = temp_dir / "usage_export.json"
        success = llm_manager.export_usage_data(str(export_file))
        
        assert success == True
        assert export_file.exists()
        
        # Clear usage data
        llm_manager.usage_history = []
        
        # Import usage data
        success = llm_manager.import_usage_data(str(export_file))
        
        assert success == True
        assert len(llm_manager.usage_history) == 1
        assert llm_manager.usage_history[0]['total_tokens'] == 100
    
    def test_concurrent_requests(self, config_manager):
        """Test handling concurrent API requests"""
        llm_manager = LLMManager(config_manager)
        
        # Test request queue management
        assert llm_manager.active_requests == 0
        assert llm_manager.max_concurrent_requests > 0
        
        # Simulate starting requests
        llm_manager._increment_active_requests()
        llm_manager._increment_active_requests()
        
        assert llm_manager.active_requests == 2
        
        # Simulate completing requests
        llm_manager._decrement_active_requests()
        assert llm_manager.active_requests == 1
        
        llm_manager._decrement_active_requests()
        assert llm_manager.active_requests == 0
    
    def test_request_timeout_handling(self, config_manager):
        """Test request timeout configuration and handling"""
        llm_manager = LLMManager(config_manager)
        
        # Test timeout configuration
        llm_manager.set_request_timeout(30)
        assert llm_manager.request_timeout == 30
        
        # Test invalid timeout
        with pytest.raises(ValueError):
            llm_manager.set_request_timeout(-1)
        
        with pytest.raises(ValueError):
            llm_manager.set_request_timeout(0)
    
    def test_model_validation(self, config_manager):
        """Test model validation for different providers"""
        llm_manager = LLMManager(config_manager)
        
        # Test valid OpenAI models
        assert llm_manager.is_valid_model(LLMProvider.OPENAI, "gpt-4o") == True
        assert llm_manager.is_valid_model(LLMProvider.OPENAI, "gpt-3.5-turbo") == True
        
        # Test invalid model
        assert llm_manager.is_valid_model(LLMProvider.OPENAI, "invalid-model") == False
        
        # Test getting available models
        models = llm_manager.get_available_models(LLMProvider.OPENAI)
        assert len(models) > 0
        assert "gpt-4o" in models
        assert "gpt-3.5-turbo" in models
    
    def test_image_preprocessing(self, config_manager, temp_dir):
        """Test image preprocessing for OCR"""
        llm_manager = LLMManager(config_manager)
        
        # Create test image file
        image_file = temp_dir / "test.png"
        image_file.write_bytes(b"fake image data")
        
        # Test image validation
        assert llm_manager.is_valid_image(str(image_file)) == True
        
        # Test unsupported format
        text_file = temp_dir / "test.txt"
        text_file.write_text("not an image")
        
        assert llm_manager.is_valid_image(str(text_file)) == False
        
        # Test image size limits
        assert llm_manager.check_image_size(str(image_file)) == True
    
    def test_retry_logic(self, config_manager):
        """Test retry logic for failed requests"""
        llm_manager = LLMManager(config_manager)
        
        # Test retry configuration
        llm_manager.set_retry_config(max_retries=3, backoff_factor=2.0)
        
        assert llm_manager.max_retries == 3
        assert llm_manager.backoff_factor == 2.0
        
        # Test exponential backoff calculation
        delays = []
        for i in range(3):
            delay = llm_manager.calculate_backoff_delay(i)
            delays.append(delay)
        
        # Each delay should be longer than the previous
        assert delays[1] > delays[0]
        assert delays[2] > delays[1]
    
    def test_usage_data_persistence(self, config_manager):
        """Test persistent storage of usage data"""
        llm_manager = LLMManager(config_manager)
        
        # Add usage data
        usage = {
            'timestamp': datetime.now().isoformat(),
            'provider': 'openai',
            'total_tokens': 100
        }
        llm_manager.usage_history.append(usage)
        
        # Save usage data
        llm_manager.save_usage_data()
        
        # Create new instance and load data
        new_llm_manager = LLMManager(config_manager)
        new_llm_manager.load_usage_data()
        
        assert len(new_llm_manager.usage_history) >= 1
    
    def test_cleanup(self, config_manager):
        """Test proper cleanup of resources"""
        llm_manager = LLMManager(config_manager)
        
        # Set some state
        llm_manager.usage_history = [{'test': 'data'}]
        llm_manager.active_requests = 2
        
        # Cleanup
        llm_manager.cleanup()
        
        # State should be cleaned
        assert llm_manager.active_requests == 0
        assert llm_manager.api_client is None
        
        # Should not raise errors on second cleanup
        llm_manager.cleanup()