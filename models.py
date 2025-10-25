from sqlalchemy import Column, Integer, String, JSON
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class TwitterUser(Base):
    __tablename__ = "twitter_users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    twitter_id = Column(String, unique=True, nullable=False)
    name = Column(String)
    username = Column(String)
    description = Column(String)
    public_metrics = Column(JSON)
