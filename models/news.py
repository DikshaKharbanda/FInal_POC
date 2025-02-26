from pydantic import BaseModel
from typing import List

class NewsArticle(BaseModel):
    title: str
    summary: str
    link: str
    source: str

class NewsCollection(BaseModel):  # Add wrapper model
    news: List[NewsArticle]
