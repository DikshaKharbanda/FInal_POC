# models/news_models.py
from pydantic import BaseModel

class NewsArticle(BaseModel):
    title: str
    link: str
    snippet: str
    source: str

class NewsCollection(BaseModel):
    news: list[NewsArticle]
