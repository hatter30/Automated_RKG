"""Application settings loaded from environment variables."""
from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Keys
    openai_api_key: str
    brave_search_api_key: str
    github_token: str | None = None  # Optional: for higher rate limits on GitHub API

    @field_validator('openai_api_key', 'brave_search_api_key')
    @classmethod
    def validate_api_key(cls, v: str, info) -> str:
        """Validate API keys are not empty and have minimum length."""
        if not v or not v.strip():
            raise ValueError(f"{info.field_name} cannot be empty")

        v = v.strip()

        if len(v) < 20:
            raise ValueError(
                f"{info.field_name} appears invalid (too short). "
                f"Expected at least 20 characters, got {len(v)}"
            )

        # Check for placeholder values
        placeholder_patterns = ['your_key', 'replace_me', 'api_key_here', 'xxx']
        if any(pattern in v.lower() for pattern in placeholder_patterns):
            raise ValueError(
                f"{info.field_name} appears to be a placeholder. "
                f"Please set a valid API key in your .env file"
            )

        return v

    # OpenAI Configuration
    openai_model: str = "gpt-4-turbo-preview"

    # Search Configuration
    max_search_results: int = 10
    max_queries_per_topic: int = 5
    max_github_code_results: int = 3  # Number of code examples to fetch from GitHub

    # Output Configuration
    output_dir: str = "output/logseq"

    # Concept Filtering
    relevance_threshold: float = 0.5
    max_concepts: int = 20

    # Entity Extraction
    entity_batch_size: int = 10

    # Logging
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Singleton instance
_settings: Settings | None = None


def get_settings() -> Settings:
    """Get application settings singleton."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
