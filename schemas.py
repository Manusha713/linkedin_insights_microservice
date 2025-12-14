from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import List, Optional


class PostBase(BaseModel):
    """Schema for a post before insertion (used by scraper/create)."""
    content: str
    likes_count: int
    comments_count: int
    timestamp: datetime

class Post(PostBase):
    id: int
    page_id: str
    class Config:
        from_attributes = True

class PageBase(BaseModel):
    page_id: str  
    name: str
    description: str
    website: Optional[HttpUrl] = None
    industry: str
    total_followers: int
    head_count: Optional[int] = None

class Page(PageBase):
    """Full Page schema returned by the GET /pages/{page_id} endpoint."""
    id: int
    scrape_timestamp: datetime
    
    recent_posts: List[Post] = []
    
    class Config:
        from_attributes = True
        
class PageCreate(PageBase):
    posts_data: List[PostBase] = []