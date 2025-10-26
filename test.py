from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd

# -----------------------------
# CONFIG
# -----------------------------
TWITTER_USERNAME = "imVkohli"  # Change this to any username
SCROLL_PAUSE_TIME = 2          # Pause between scrolls
MAX_TWEETS = 50                # Max tweets to fetch

# -----------------------------
# SETUP CHROME DRIVER
# -----------------------------
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in background
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# -----------------------------
# OPEN TWITTER PAGE
# -----------------------------
url = f"https://twitter.com/{TWITTER_USERNAME}"
driver.get(url)
time.sleep(5)  # Wait for page to load

# -----------------------------
# SCROLL AND COLLECT TWEETS
# -----------------------------
tweets = []
last_height = driver.execute_script("return document.body.scrollHeight")

while len(tweets) < MAX_TWEETS:
    elements = driver.find_elements(By.XPATH, '//div[@data-testid="tweetText"]')
    for elem in elements:
        text = elem.text
        if text not in tweets:
            tweets.append(text)
            if len(tweets) >= MAX_TWEETS:
                break

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(SCROLL_PAUSE_TIME)
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

driver.quit()

# -----------------------------
# SAVE TWEETS TO CSV
# -----------------------------
df = pd.DataFrame(tweets, columns=["Tweet"])
df.to_csv(f"{TWITTER_USERNAME}_tweets.csv", index=False)
print(f"Saved {len(tweets)} tweets to {TWITTER_USERNAME}_tweets.csv")


