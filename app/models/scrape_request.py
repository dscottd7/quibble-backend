from pydantic import BaseModel, HttpUrl
from typing import Optional


class ScrapeRequest(BaseModel):
    url: HttpUrl
    # selector: Optional[str] = None
    requires_javascript: bool = False
