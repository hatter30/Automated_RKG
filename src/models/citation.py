"""Citation data model for source references."""
from pydantic import BaseModel, HttpUrl, Field
from typing import Optional
from datetime import datetime


class Citation(BaseModel):
    """Represents a source citation for facts."""

    url: HttpUrl
    title: str
    snippet: Optional[str] = None
    accessed_at: datetime = Field(default_factory=datetime.utcnow)

    def to_markdown(self) -> str:
        """Format citation as markdown link."""
        return f"[{self.title}]({self.url})"
