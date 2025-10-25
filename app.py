import time
import tweepy
from config import BEARER_TOKEN, engine
from sqlalchemy.orm import sessionmaker
from models import Base, TwitterUser

# --------------------------------------------------
# 1️⃣ Initialize Tweepy client
# --------------------------------------------------
client = tweepy.Client(bearer_token=BEARER_TOKEN)

# --------------------------------------------------
# 2️⃣ Initialize Database
# --------------------------------------------------
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# --------------------------------------------------
# 3️⃣ Function: Fetch and Store User Info
# --------------------------------------------------
def get_user_info(username: str):
    """
    Fetch user info from Twitter, print it, and store it in the database.
    Handles rate limits (429 errors) by waiting.
    """
    while True:
        try:
            # Request user data
            response = client.get_user(
                username=username,
                user_fields=["id", "name", "username", "description", "public_metrics"]
            )

            if response.data:
                user = response.data
                print("User info:")
                print(f"ID: {user.id}")
                print(f"Name: {user.name}")
                print(f"Username: {user.username}")
                print(f"Description: {user.description}")
                print(f"Followers: {user.public_metrics['followers_count']}")
                print(f"Following: {user.public_metrics['following_count']}")
                print(f"Tweet Count: {user.public_metrics['tweet_count']}")

                # Save to database
                new_user = TwitterUser(
                    twitter_id=user.id,
                    name=user.name,
                    username=user.username,
                    description=user.description,
                    public_metrics=user.public_metrics
                )

                session.merge(new_user)  # prevents duplicate entries
                session.commit()
                print(f"✅ User '{user.username}' saved to database successfully.")
            else:
                print("No user data found.")

            break  # exit loop if successful

        except tweepy.TooManyRequests:
            print("Rate limit reached. Waiting 15 minutes...")
            time.sleep(15 * 60)  # wait 15 minutes before retry

        except Exception as e:
            print("An error occurred:", e)
            break

# --------------------------------------------------
# 4️⃣ Main Execution
# --------------------------------------------------
if __name__ == "__main__":
    username_to_fetch = "snigs98"  # Replace with any Twitter username
    get_user_info(username_to_fetch)
