# app.py
from fetch_tweets import fetch_all_tweets
from config import Base, engine
from display import DisplayManager

def setup_db():
    Base.metadata.create_all(bind=engine)

def main():
    setup_db()
    fetch_all_tweets()
    display = DisplayManager()
    display.run()

if __name__ == "__main__":
    main()
