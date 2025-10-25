import os
from dotenv import load_dotenv

load_dotenv()
BEARER_TOKEN = os.getenv("BEARER_TOKEN")
print("Bearer Token:", BEARER_TOKEN)
# type: ignore
from sqlalchemy import create_engine


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///twitter_data.db")

# Initialize SQLAlchemy engine
engine = create_engine(DATABASE_URL)