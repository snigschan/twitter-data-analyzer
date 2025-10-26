from flask import Flask, render_template, request
from models import Tweet
from config import SessionLocal
import qrcode
import io
import base64

app = Flask(__name__)
session = SessionLocal()

def generate_qr_base64(url):
    """Generate QR code and return as base64 string for HTML img tag."""
    qr_img = qrcode.make(url)
    buf = io.BytesIO()
    qr_img.save(buf, format='PNG')
    buf.seek(0)
    img_b64 = base64.b64encode(buf.read()).decode('ascii')
    return f"data:image/png;base64,{img_b64}"

@app.route("/")
def home():
    """Show menu of unique Twitter handles."""
    handles = sorted({t.username for t in session.query(Tweet).all()})
    return render_template("index.html", handles=handles)

@app.route("/tweets")
def show_tweets():
    """Show tweets for selected handle with QR code."""
    username = request.args.get("username")
    if not username:
        return "No username selected!", 400

    tweets = session.query(Tweet).filter_by(username=username).order_by(Tweet.created_at.desc()).all()
    qr_code = generate_qr_base64(f"https://twitter.com/{username}")

    return render_template("tweets.html", username=username, tweets=tweets, qr_code=qr_code)

if __name__ == "__main__":
    app.run(debug=True)
