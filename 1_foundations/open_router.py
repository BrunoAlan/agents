"""
OpenRouter API Client Class

This module provides a class to interact with the OpenRouter API,
which serves as a gateway to multiple LLM providers including OpenAI,
Anthropic, Google, Meta, and many others.

OpenRouter offers:
- Access to many free models
- Simple billing for paid models
- OpenAI-compatible API interface
- Easy model switching
"""

import os
from typing import List, Dict, Any, Optional, Union
from openai import OpenAI, AsyncOpenAI
from dotenv import load_dotenv
from IPython.display import display, Markdown
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OpenRouterClient:
    """
    A client class for interacting with the OpenRouter API.

    OpenRouter provides access to multiple LLM providers through
    a single OpenAI-compatible interface.
    """

    BASE_URL = "https://openrouter.ai/api/v1"

    # Popular free models available on OpenRouter
    FREE_MODELS = {
        "mistral_small": "mistralai/mistral-small-3.1-24b-instruct:free",
        "deepseek_v3": "deepseek/deepseek-v3-base:free",
        "llama_4_maverick": "meta-llama/llama-4-maverick:free",
        "hermes_mistral": "nousresearch/deephermes-3-mistral-24b-preview:free",
        "gemini_2_flash": "google/gemini-2.0-flash-exp:free",
    }

    # Popular paid models (usually more capable)
    PAID_MODELS = {
        "gpt_4_nano": "openai/gpt-4.1-nano",
        "gpt_4_mini": "openai/gpt-4.1-mini",
        "claude_haiku": "anthropic/claude-3.5-haiku",
        "claude_sonnet": "anthropic/claude-3.7-sonnet",
        "gemini_flash_thinking": "google/gemini-2.5-flash-preview:thinking",
    }

    def __init__(self, api_key: Optional[str] = None, load_env: bool = True):
        """
        Initialize the OpenRouter client.

        Args:
            api_key: OpenRouter API key. If None, will try to load from environment
            load_env: Whether to load environment variables from .env file
        """
        if load_env:
            load_dotenv(override=True)

        self.api_key = api_key or os.getenv("OPEN_ROUTER_API_KEY")
        print(self.api_key)

        if not self.api_key:
            raise ValueError(
                "OpenRouter API key not found. Please provide it as parameter "
                "or set OPEN_ROUTER_API_KEY environment variable. "
                "Get your key from: https://openrouter.ai"
            )

        logger.info(f"OpenRouter API Key loaded (starts with: {self.api_key[:8]}...)")

        # Initialize OpenAI clients with OpenRouter base URL
        self.client = OpenAI(api_key=self.api_key, base_url=self.BASE_URL)

        self.async_client = AsyncOpenAI(api_key=self.api_key, base_url=self.BASE_URL)

        # Chat history for conversation context
        self.chat_history: List[Dict[str, str]] = []

    def get_available_models(self) -> Dict[str, Dict[str, str]]:
        """
        Get available models organized by type (free/paid).

        Returns:
            Dictionary with 'free' and 'paid' model categories
        """
        return {"free": self.FREE_MODELS, "paid": self.PAID_MODELS}

    def list_models(self, show_free: bool = True, show_paid: bool = True) -> None:
        """
        Print available models in a readable format.

        Args:
            show_free: Whether to show free models
            show_paid: Whether to show paid models
        """
        if show_free:
            print("🆓 FREE MODELS:")
            for name, model_id in self.FREE_MODELS.items():
                print(f"  • {name}: {model_id}")
            print()

        if show_paid:
            print("💰 PAID MODELS:")
            for name, model_id in self.PAID_MODELS.items():
                print(f"  • {name}: {model_id}")
            print()

    def chat(
        self,
        message: str,
        model: str = "meta-llama/llama-4-maverick:free",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        display_response: bool = True,
    ) -> str:
        """
        Send a chat message and get a response.

        Args:
            message: The user message to send
            model: Model to use (can use friendly name or full model ID)
            temperature: Sampling temperature (0.0 to 2.0)
            max_tokens: Maximum tokens in response (None for default)
            display_response: Whether to display response in Markdown format

        Returns:
            The assistant's response as a string
        """
        # Convert friendly name to model ID if needed
        model_id = self._resolve_model_name(model)

        # Add user message to history
        self.chat_history.append({"role": "user", "content": message})

        try:
            # Create completion
            completion_kwargs = {
                "model": model_id,
                "messages": self.chat_history,
                "temperature": temperature,
            }

            if max_tokens:
                completion_kwargs["max_tokens"] = max_tokens

            response = self.client.chat.completions.create(**completion_kwargs)

            # Extract response text
            assistant_response = response.choices[0].message.content

            # Add to history
            self.chat_history.append(
                {"role": "assistant", "content": assistant_response}
            )

            # Display if requested
            if display_response:
                display(
                    Markdown(f"**Assistant ({model_id}):**\n\n{assistant_response}")
                )

            return assistant_response

        except Exception as e:
            logger.error(f"Error calling OpenRouter API: {e}")
            raise

    async def chat_async(
        self,
        message: str,
        model: str = "meta-llama/llama-4-maverick:free",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Asynchronous version of chat method.

        Args:
            message: The user message to send
            model: Model to use (can use friendly name or full model ID)
            temperature: Sampling temperature (0.0 to 2.0)
            max_tokens: Maximum tokens in response (None for default)

        Returns:
            The assistant's response as a string
        """
        model_id = self._resolve_model_name(model)

        self.chat_history.append({"role": "user", "content": message})

        try:
            completion_kwargs = {
                "model": model_id,
                "messages": self.chat_history,
                "temperature": temperature,
            }

            if max_tokens:
                completion_kwargs["max_tokens"] = max_tokens

            response = await self.async_client.chat.completions.create(
                **completion_kwargs
            )

            assistant_response = response.choices[0].message.content
            self.chat_history.append(
                {"role": "assistant", "content": assistant_response}
            )

            return assistant_response

        except Exception as e:
            logger.error(f"Error calling OpenRouter API (async): {e}")
            raise

    def get_response(
        self,
        message: str,
        model: str = "meta-llama/llama-4-maverick:free",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Get a response without managing chat history or display.
        Useful for one-off queries.

        Args:
            message: The user message to send
            model: Model to use (can use friendly name or full model ID)
            temperature: Sampling temperature (0.0 to 2.0)
            max_tokens: Maximum tokens in response (None for default)

        Returns:
            The assistant's response as a string
        """
        model_id = self._resolve_model_name(model)

        try:
            completion_kwargs = {
                "model": model_id,
                "messages": [{"role": "user", "content": message}],
                "temperature": temperature,
            }

            if max_tokens:
                completion_kwargs["max_tokens"] = max_tokens

            response = self.client.chat.completions.create(**completion_kwargs)

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Error calling OpenRouter API: {e}")
            raise

    def compare_models(
        self, prompt: str, models: List[str], temperature: float = 0.7
    ) -> Dict[str, str]:
        """
        Compare responses from multiple models for the same prompt.

        Args:
            prompt: The prompt to send to all models
            models: List of model names/IDs to compare
            temperature: Sampling temperature for all requests

        Returns:
            Dictionary mapping model names to their responses
        """
        results = {}

        for model in models:
            try:
                logger.info(f"Getting response from {model}...")
                response = self.get_response(prompt, model, temperature)
                results[model] = response
            except Exception as e:
                logger.error(f"Error with model {model}: {e}")
                results[model] = f"Error: {str(e)}"

        return results

    def clear_history(self) -> None:
        """Clear the chat history. This action cannot be undone."""
        self.chat_history.clear()
        logger.info("Chat history cleared")

    def get_history(self) -> List[Dict[str, str]]:
        """Get a copy of the current chat history."""
        return self.chat_history.copy()

    def set_history(self, history: List[Dict[str, str]]) -> None:
        """
        Set the chat history to a specific state.

        Args:
            history: List of message dictionaries with 'role' and 'content' keys
        """
        self.chat_history = history.copy()

    def export_conversation(self, filename: str) -> None:
        """
        Export the current conversation to a file.

        Args:
            filename: Path to save the conversation
        """
        import json

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.chat_history, f, indent=2, ensure_ascii=False)

        logger.info(f"Conversation exported to {filename}")

    def load_conversation(self, filename: str) -> None:
        """
        Load a conversation from a file.

        Args:
            filename: Path to load the conversation from
        """
        import json

        with open(filename, "r", encoding="utf-8") as f:
            self.chat_history = json.load(f)

        logger.info(f"Conversation loaded from {filename}")

    def _resolve_model_name(self, model: str) -> str:
        """
        Resolve a friendly model name to the full model ID.

        Args:
            model: Model name (friendly name or full ID)

        Returns:
            Full model ID for the API
        """
        # Check if it's a friendly name
        all_models = {**self.FREE_MODELS, **self.PAID_MODELS}
        if model in all_models:
            return all_models[model]

        # Assume it's already a full model ID
        return model

    def get_client(self) -> OpenAI:
        """Get the underlying OpenAI client for advanced usage."""
        return self.client

    def get_async_client(self) -> AsyncOpenAI:
        """Get the underlying async OpenAI client for advanced usage."""
        return self.async_client


# Convenience functions for backward compatibility and quick usage
def create_client(api_key: Optional[str] = None) -> OpenRouterClient:
    """
    Create an OpenRouter client instance.

    Args:
        api_key: OpenRouter API key (optional, can use environment variable)

    Returns:
        Configured OpenRouterClient instance
    """
    return OpenRouterClient(api_key=api_key)


def quick_chat(
    message: str,
    model: str = "meta-llama/llama-4-maverick:free",
    api_key: Optional[str] = None,
) -> str:
    """
    Quick one-off chat without creating a persistent client.

    Args:
        message: The message to send
        model: Model to use
        api_key: OpenRouter API key (optional)

    Returns:
        The model's response
    """
    client = create_client(api_key)
    return client.get_response(message, model)


# Example usage
if __name__ == "__main__":
    # Create client
    client = OpenRouterClient()

    # List available models
    client.list_models()

    # Simple chat
    response = client.chat("What is 2+2?", model="mistral_small")
    print(f"Response: {response}")

    # Compare models
    results = client.compare_models(
        "Explain artificial intelligence in one sentence",
        ["mistral_small", "llama_4_maverick", "gemini_2_flash"],
    )

    for model, response in results.items():
        print(f"\n{model}: {response}")
