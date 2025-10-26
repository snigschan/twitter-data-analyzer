# fetch_tweets.py
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from config import TWITTER_HANDLES, MAX_TWEETS, SessionLocal
from models import Tweet
from datetime import datetime

# Keep this variable, but don’t actually use it
TWITTER_API_KEY = "YOUR_TWITTER_BEARER_TOKEN"

def validate_handle(handle):
    return handle.isalnum() or "_" in handle

def get_driver(headless=True):
    """Initialize Chrome WebDriver."""
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)
    return driver

def fetch_tweets_for_handle(handle):
    """Fetch tweets from a public Twitter profile using Selenium."""
    session = SessionLocal()
    driver = get_driver(headless=True)

    print(f"Fetching tweets for @{handle} ...")

    try:
        driver.get(f"https://twitter.com/{handle}")
        time.sleep(5)

        # Scroll and collect tweets
        tweet_texts = set()
        last_height = driver.execute_script("return document.body.scrollHeight")
        while len(tweet_texts) < MAX_TWEETS:
            tweets = driver.find_elements(By.XPATH, "//article//div[@data-testid='tweetText']")
            for t in tweets:
                text = t.text.strip()
                if text:
                    tweet_texts.add(text)
                if len(tweet_texts) >= MAX_TWEETS:
                    break

            # Scroll down
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        # Store tweets in DB (deduplication handled)
        for text in list(tweet_texts)[:MAX_TWEETS]:
            exists = session.query(Tweet).filter_by(content=text, username=handle).first()
            if not exists:
                new_tweet = Tweet(
                    tweet_id=f"{handle}_{hash(text)}",  # synthetic ID
                    username=handle,
                    content=text,
                    created_at=datetime.utcnow()
                )
                session.add(new_tweet)
        session.commit()
        print(f"✅ Saved {len(tweet_texts)} tweets for @{handle}")

    except Exception as e:
        print(f"❌ Error fetching tweets for @{handle}: {e}")

    finally:
        driver.quit()
        session.close()

def fetch_all_tweets():
    print("Performing initial  fetch (this may take a while)...")
    for handle in TWITTER_HANDLES:
        if validate_handle(handle):
            fetch_tweets_for_handle(handle)
    print("✅ All tweets fetched ")
