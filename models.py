from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

class Page(Base):
    __tablename__ = 'pages'
    id = Column(Integer, primary_key=True, index=True)
    page_id = Column(String, unique=True, index=True) 
    name = Column(String, index=True)
    description = Column(Text)
    website = Column(String, nullable=True)
    industry = Column(String, index=True)
    total_followers = Column(Integer, index=True)
    head_count = Column(Integer, nullable=True) # Retaining basic required fields
    scrape_timestamp = Column(DateTime, default=datetime.utcnow)
    posts = relationship("Post", back_populates="page")

class Post(Base):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True, index=True)
    page_id = Column(String, ForeignKey('pages.page_id')) 
    content = Column(Text)
    likes_count = Column(Integer)
    comments_count = Column(Integer)
    timestamp = Column(DateTime)
    page = relationship("Page", back_populates="posts")
    