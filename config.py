# config.py
# ---------------------------------
# Twitter Fetch Configuration
# ---------------------------------
TWITTER_HANDLES = ["imVkohli", "BCCI", "ICC", "RCBTweets", "ESPNcricinfo"]
SCROLL_PAUSE_TIME = 2
MAX_TWEETS = 30
HEADLESS = True

# ---------------------------------
# Display Configuration
# ---------------------------------
DISPLAY_REFRESH_INTERVAL = 3600  # seconds (1 hour)
DISPLAY_FONT = "arial"
DISPLAY_TITLE_SIZE = 60
DISPLAY_BODY_SIZE = 42

# ---------------------------------
# Database Configuration
# ---------------------------------
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///twitter_data.db"
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()
