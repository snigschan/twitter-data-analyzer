from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class TwitterUser(Base):
    __tablename__ = "twitter_users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    twitter_id = Column(String, unique=True, nullable=False)
    name = Column(String)
    username = Column(String)
    description = Column(String)
    public_metrics = Column(JSON)

    # Relationship to tweets
    tweets = relationship("Tweet", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<TwitterUser(username='{self.username}', name='{self.name}')>"


class Tweet(Base):
    __tablename__ = "tweets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tweet_id = Column(String, unique=True, nullable=False)
    username = Column(String)
    text = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    public_metrics = Column(JSON)
    user_id = Column(Integer, ForeignKey("twitter_users.id"))

    # Relationship back to user
    user = relationship("TwitterUser", back_populates="tweets")

    def __repr__(self):
        return f"<Tweet(id='{self.tweet_id}', username='{self.username}', text='{self.text[:30]}...')>"


class DisplayedTweet(Base):
    __tablename__ = "displayed_tweets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tweet_id = Column(String, unique=True, nullable=False)
    displayed_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<DisplayedTweet(tweet_id='{self.tweet_id}', displayed_at='{self.displayed_at}')>"
