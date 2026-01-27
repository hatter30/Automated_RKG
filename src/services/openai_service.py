"""Service for interacting with OpenAI API."""
from openai import OpenAI, AsyncOpenAI
from typing import Optional
import logging
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class OpenAIService:
    """Service for interacting with OpenAI API."""

    def __init__(self, api_key: str, model: str = "gpt-4-turbo-preview"):
        self.client = OpenAI(api_key=api_key)
        self.async_client = AsyncOpenAI(api_key=api_key)
        self.model = model

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def generate_completion(
        self, system_prompt: str, user_prompt: str, temperature: float = 0.7
    ) -> str:
        """
        Generate a completion with retry logic.

        Args:
            system_prompt: System message to set context
            user_prompt: User message with the actual request
            temperature: Sampling temperature (0.0-2.0)

        Returns:
            Generated text response
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
            )
            return response.choices[0].message.content or ""

        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def generate_structured_output(
        self, system_prompt: str, user_prompt: str, temperature: float = 0.7
    ) -> str:
        """
        Generate JSON-formatted output.

        Args:
            system_prompt: System message to set context
            user_prompt: User message with the actual request
            temperature: Sampling temperature (0.0-2.0)

        Returns:
            Generated JSON string response
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
                response_format={"type": "json_object"},
            )
            return response.choices[0].message.content or "{}"

        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def generate_completion_async(
        self, system_prompt: str, user_prompt: str, temperature: float = 0.7
    ) -> str:
        """
        Generate a completion asynchronously with retry logic.

        Args:
            system_prompt: System message to set context
            user_prompt: User message with the actual request
            temperature: Sampling temperature (0.0-2.0)

        Returns:
            Generated text response
        """
        try:
            response = await self.async_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
            )
            return response.choices[0].message.content or ""

        except Exception as e:
            logger.error(f"OpenAI async API call failed: {e}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def generate_structured_output_async(
        self, system_prompt: str, user_prompt: str, temperature: float = 0.7
    ) -> str:
        """
        Generate JSON-formatted output asynchronously.

        Args:
            system_prompt: System message to set context
            user_prompt: User message with the actual request
            temperature: Sampling temperature (0.0-2.0)

        Returns:
            Generated JSON string response
        """
        try:
            response = await self.async_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
                response_format={"type": "json_object"},
            )
            return response.choices[0].message.content or "{}"

        except Exception as e:
            logger.error(f"OpenAI async API call failed: {e}")
            raise
