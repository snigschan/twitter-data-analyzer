import time
import re
import pandas as pd
import snscrape.modules.twitter as sntwitter
from config import engine
from sqlalchemy.orm import sessionmaker
from models import Base, TwitterUser, Tweet, DisplayedTweet
from sqlalchemy.exc import IntegrityError

# --------------------------------------------------
# 1️⃣ Initialize Database
# --------------------------------------------------
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

print(f"📁 Using database: {engine.url}")

# --------------------------------------------------
# 2️⃣ Helper: Validate Twitter handle
# --------------------------------------------------
def validate_handle(username: str) -> bool:
    username = username.strip().lstrip("@")
    pattern = r"^[A-Za-z0-9_]{1,15}$"
    if not re.match(pattern, username):
        print(f"❌ Invalid handle format: {username}")
        return False
    return True

# --------------------------------------------------
# 3️⃣ Fetch and Store User Info
# --------------------------------------------------
def get_user_info(username: str):
    username = username.strip().lstrip("@")
    try:
        # Using snscrape to get user info
        scraper = sntwitter.TwitterUserScraper(username)
        first_tweet = next(scraper.get_items(), None)

        if first_tweet is None:
            print(f"❌ No tweets found for @{username}, user may not exist or is private.")
            return None

        # Store basic info
        existing_user = session.query(TwitterUser).filter_by(username=username).first()
        if existing_user:
            db_user = existing_user
        else:
            db_user = TwitterUser(
                twitter_id=username,  # we don't have numeric ID, using handle as unique
                name=username,
                username=username,
                description="",
                public_metrics=None
            )
            session.add(db_user)
            session.commit()

        print(f"✅ User '{username}' saved/updated successfully.")
        return db_user

    except Exception as e:
        print(f"⚠️ Error fetching user info for {username}:", e)
        session.rollback()
        return None

# --------------------------------------------------
# 4️⃣ Fetch Tweets for a User
# --------------------------------------------------
def fetch_tweets_for_user(username: str, max_tweets: int = 100):
    username = username.strip().lstrip("@")
    if not validate_handle(username):
        return

    db_user = session.query(TwitterUser).filter_by(username=username).first()
    if not db_user:
        db_user = get_user_info(username)
        if not db_user:
            return

    print(f"\n📥 Fetching tweets for: @{username} ...")
    total_new = 0

    try:
        for i, tweet in enumerate(sntwitter.TwitterUserScraper(username).get_items()):
            if i >= max_tweets:
                break

            tweet_id = str(tweet.id)
            if session.query(DisplayedTweet).filter_by(tweet_id=tweet_id).first():
                continue

            new_tweet = Tweet(
                tweet_id=tweet_id,
                user_id=db_user.id,
                username=username,
                text=tweet.content,
                created_at=tweet.date,
                public_metrics=None  # snscrape does not provide full metrics like API
            )
            session.add(new_tweet)
            session.add(DisplayedTweet(tweet_id=tweet_id))

            try:
                session.commit()
                total_new += 1
            except IntegrityError:
                session.rollback()

        print(f"✅ Total new tweets stored for @{username}: {total_new}")

    except Exception as e:
        print(f"⚠️ Error fetching tweets for {username}:", e)
        session.rollback()

# --------------------------------------------------
# 5️⃣ Main: Fetch multiple users
# --------------------------------------------------
if __name__ == "__main__":
    twitter_handles = ["imVkohli", "elonmusk", "TwitterDev"]  # replace/add any handles you want
    max_tweets_per_user = 200  # change this number to fetch more tweets per user

    for handle in twitter_handles:
        fetch_tweets_for_user(handle, max_tweets=max_tweets_per_user)

    session.commit()
    session.close()
    print("💾 All changes committed and session closed.")
