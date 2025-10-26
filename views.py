from config import engine
from sqlalchemy.orm import sessionmaker
from models import Tweet, TwitterUser

# --------------------------------------------------
# 1️⃣ Initialize DB session
# --------------------------------------------------
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

# --------------------------------------------------
# 2️⃣ Choose the username to display tweets for
# --------------------------------------------------
username_to_view = "snigs98"  # change if needed

# --------------------------------------------------
# 3️⃣ Fetch user and tweets
# --------------------------------------------------
user = session.query(TwitterUser).filter_by(username=username_to_view).first()

if not user:
    print(f"❌ User '@{username_to_view}' not found in database.")
else:
    tweets = (
        session.query(Tweet)
        .filter_by(user_id=user.id)
        .order_by(Tweet.created_at.desc())
        .all()
    )

    if not tweets:
        print(f"ℹ️ No tweets found in the database for @{user.username}.")
    else:
        print(f"🧾 Found {len(tweets)} tweet(s) for @{user.username}:\n")

        for idx, t in enumerate(tweets, start=1):
            print("────────────────────────────")
            print(f"📄 Tweet {idx}")
            print(f"🕒 {t.created_at}")
            print(f"💬 {t.text}\n")
