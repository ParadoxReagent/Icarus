"""
AI Provider Abstraction Layer
Supports multiple AI providers: Anthropic, LiteLLM, OpenRouter
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class AIProvider(ABC):
    """Abstract base class for AI providers"""

    @abstractmethod
    def create_message(self, model: str, messages: List[Dict], max_tokens: int = 2000, **kwargs) -> str:
        """Create a message and return the response text"""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if this provider is properly configured"""
        pass


class AnthropicProvider(AIProvider):
    """Direct Anthropic API provider"""

    def __init__(self):
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        self.client = None

        if self.api_key:
            try:
                from anthropic import Anthropic
                self.client = Anthropic(api_key=self.api_key)
                logger.info("✓ Anthropic provider initialized")
            except ImportError:
                logger.error("anthropic package not installed. Run: pip install anthropic")
            except Exception as e:
                logger.error(f"Failed to initialize Anthropic client: {e}")

    def create_message(self, model: str, messages: List[Dict], max_tokens: int = 2000, **kwargs) -> str:
        """Create message using Anthropic API"""
        if not self.client:
            raise ValueError("Anthropic client not initialized. Check ANTHROPIC_API_KEY.")

        response = self.client.messages.create(
            model=model,
            max_tokens=max_tokens,
            messages=messages,
            **kwargs
        )

        return response.content[0].text

    def is_available(self) -> bool:
        return self.client is not None


class LiteLLMProvider(AIProvider):
    """LiteLLM unified provider supporting 100+ models"""

    def __init__(self):
        self.available = False

        try:
            import litellm
            self.litellm = litellm
            self.available = True
            logger.info("✓ LiteLLM provider initialized")
        except ImportError:
            logger.warning("litellm package not installed. Run: pip install litellm")

    def create_message(self, model: str, messages: List[Dict], max_tokens: int = 2000, **kwargs) -> str:
        """Create message using LiteLLM unified API"""
        if not self.available:
            raise ValueError("LiteLLM not installed. Run: pip install litellm")

        # LiteLLM uses OpenAI-style message format
        response = self.litellm.completion(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            **kwargs
        )

        return response.choices[0].message.content

    def is_available(self) -> bool:
        return self.available


class OpenRouterProvider(AIProvider):
    """OpenRouter provider (OpenAI-compatible API)"""

    def __init__(self):
        self.api_key = os.getenv('OPENROUTER_API_KEY')
        self.base_url = "https://openrouter.ai/api/v1"
        self.client = None

        if self.api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(
                    base_url=self.base_url,
                    api_key=self.api_key
                )
                logger.info("✓ OpenRouter provider initialized")
            except ImportError:
                logger.error("openai package not installed. Run: pip install openai")
            except Exception as e:
                logger.error(f"Failed to initialize OpenRouter client: {e}")

    def create_message(self, model: str, messages: List[Dict], max_tokens: int = 2000, **kwargs) -> str:
        """Create message using OpenRouter API"""
        if not self.client:
            raise ValueError("OpenRouter client not initialized. Check OPENROUTER_API_KEY.")

        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            **kwargs
        )

        return response.choices[0].message.content

    def is_available(self) -> bool:
        return self.client is not None


class AIProviderFactory:
    """Factory for creating AI provider instances"""

    PROVIDERS = {
        'anthropic': AnthropicProvider,
        'litellm': LiteLLMProvider,
        'openrouter': OpenRouterProvider,
    }

    @classmethod
    def create_provider(cls, provider_type: str) -> AIProvider:
        """Create an AI provider instance"""
        provider_class = cls.PROVIDERS.get(provider_type.lower())

        if not provider_class:
            available = ', '.join(cls.PROVIDERS.keys())
            raise ValueError(f"Unknown provider: {provider_type}. Available: {available}")

        return provider_class()

    @classmethod
    def get_available_providers(cls) -> List[str]:
        """Get list of configured and available providers"""
        available = []

        for provider_name, provider_class in cls.PROVIDERS.items():
            try:
                provider = provider_class()
                if provider.is_available():
                    available.append(provider_name)
            except Exception as e:
                logger.debug(f"Provider {provider_name} not available: {e}")

        return available


class AIClient:
    """
    Unified AI client that automatically selects provider based on configuration.
    Supports multiple models with different providers for red/blue teams.
    """

    def __init__(self, provider_type: str = None, model: str = None):
        """
        Initialize AI client with optional provider and model.

        Args:
            provider_type: Provider to use (anthropic, litellm, openrouter)
            model: Model name/identifier
        """
        # Auto-detect provider if not specified
        if not provider_type:
            provider_type = self._auto_detect_provider(model)

        self.provider_type = provider_type
        self.model = model
        self.provider = AIProviderFactory.create_provider(provider_type)

        if not self.provider.is_available():
            raise ValueError(f"Provider {provider_type} is not properly configured")

        logger.info(f"AI Client initialized: provider={provider_type}, model={model}")

    def _auto_detect_provider(self, model: str = None) -> str:
        """
        Auto-detect provider based on model name or environment variables.

        Priority:
        1. Model prefix (e.g., "openai/gpt-4" -> litellm)
        2. Environment variables (ANTHROPIC_API_KEY -> anthropic)
        3. Default to anthropic if available
        """
        if model:
            # LiteLLM models have provider/ prefix
            if '/' in model:
                logger.info(f"Detected LiteLLM model format: {model}")
                return 'litellm'

            # OpenRouter models often have organization prefixes
            if model.startswith(('openai/', 'anthropic/', 'google/', 'meta-llama/')):
                logger.info(f"Detected OpenRouter model format: {model}")
                return 'openrouter'

        # Check environment variables
        if os.getenv('OPENROUTER_API_KEY'):
            logger.info("Found OPENROUTER_API_KEY, using OpenRouter")
            return 'openrouter'

        if os.getenv('ANTHROPIC_API_KEY'):
            logger.info("Found ANTHROPIC_API_KEY, using Anthropic")
            return 'anthropic'

        # Default fallback
        logger.warning("No provider detected, defaulting to anthropic")
        return 'anthropic'

    def create_message(self, messages: List[Dict], max_tokens: int = 2000, **kwargs) -> str:
        """
        Create a message using the configured provider and model.

        Args:
            messages: List of message dicts with 'role' and 'content'
            max_tokens: Maximum tokens in response
            **kwargs: Additional provider-specific parameters

        Returns:
            Response text from the AI model
        """
        if not self.model:
            raise ValueError("Model not specified. Set model during initialization or via environment.")

        return self.provider.create_message(
            model=self.model,
            messages=messages,
            max_tokens=max_tokens,
            **kwargs
        )

    @staticmethod
    def from_env(env_prefix: str = '') -> 'AIClient':
        """
        Create AI client from environment variables.

        Looks for:
        - {env_prefix}_PROVIDER (e.g., RED_TEAM_PROVIDER)
        - {env_prefix}_MODEL (e.g., RED_TEAM_MODEL)

        Args:
            env_prefix: Prefix for environment variables (e.g., 'RED_TEAM', 'BLUE_TEAM')

        Returns:
            Configured AIClient instance
        """
        provider_key = f"{env_prefix}_PROVIDER" if env_prefix else "AI_PROVIDER"
        model_key = f"{env_prefix}_MODEL" if env_prefix else "AI_MODEL"

        provider = os.getenv(provider_key, '').strip()
        model = os.getenv(model_key, '').strip()

        if not model:
            raise ValueError(f"Model not specified in {model_key} environment variable")

        # If provider not specified, auto-detect
        provider = provider if provider else None

        return AIClient(provider_type=provider, model=model)


def test_providers():
    """Test all available providers"""
    print("\n=== Testing AI Providers ===\n")

    available = AIProviderFactory.get_available_providers()
    print(f"Available providers: {', '.join(available) if available else 'None'}\n")

    for provider_name in available:
        try:
            provider = AIProviderFactory.create_provider(provider_name)
            print(f"✓ {provider_name}: Configured and ready")
        except Exception as e:
            print(f"✗ {provider_name}: {e}")

    print("\n=== Environment Variables ===\n")
    env_vars = [
        'ANTHROPIC_API_KEY',
        'OPENROUTER_API_KEY',
        'OPENAI_API_KEY',
        'RED_TEAM_PROVIDER',
        'RED_TEAM_MODEL',
        'BLUE_TEAM_PROVIDER',
        'BLUE_TEAM_MODEL',
    ]

    for var in env_vars:
        value = os.getenv(var)
        if value:
            # Mask API keys
            if 'KEY' in var:
                display = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else "***"
            else:
                display = value
            print(f"  {var}: {display}")
        else:
            print(f"  {var}: (not set)")


if __name__ == "__main__":
    # Run tests when executed directly
    test_providers()
