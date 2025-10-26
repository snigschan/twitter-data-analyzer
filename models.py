# models.py
from sqlalchemy import Column, Integer, String, Text, DateTime, UniqueConstraint
from datetime import datetime
from config import Base

class Tweet(Base):
    __tablename__ = "tweets"

    id = Column(Integer, primary_key=True, index=True)
    tweet_id = Column(String, unique=True, index=True)
    username = Column(String, index=True)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (UniqueConstraint('tweet_id', name='_tweet_id_uc'),)
