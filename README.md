# twitter-data-analyzer
Desktop and web application for analyzing and displaying tweets with QR codes
# Twitter Data Analyzer

Desktop and web application for analyzing and displaying tweets with QR codes.

---

## Author
**snigs98**

---

## Project Overview

This project allows users to:

- Fetch tweets from Twitter accounts using the Twitter API.
- Store tweets in a local database.
- Display tweets in a **desktop application** using Pygame:
  - Select Twitter handles.
  - Navigate tweets with previous/next buttons.
  - View QR codes linking to the Twitter profile.
- Display tweets in a **web application**:
  - Select a Twitter handle from the homepage.
  - View all tweets for that handle with timestamp and QR code.
  
---

## Features

- Desktop GUI built with **Pygame**.
- Web interface built with **Flask** and HTML templates.
- Supports multiple Twitter handles.
- Automatic hourly refresh for new tweets (desktop app).
- QR code generation for each Twitter handle.

---

## Setup Instructions

1. **Clone the repository**
```bash


# 1. Go into the project folder
cd twitter-data-analyzer

# 2. Activate your virtual environment
# Windows
venv\Scripts\activate
# Linux / Mac
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Make sure your .env file has the correct Twitter API credentials

# 5. Run the web application
python web_app.py
Open the web app in your browser:

Go to: http://127.0.0.1:5000

The homepage will show available Twitter handles.

Click a handle to see its tweets along with the QR code.
git clone https://github.com/snigschan/twitter-data-analyzer.git
cd twitter-data-analyzer
