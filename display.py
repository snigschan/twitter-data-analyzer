import argparse
import time
import qrcode
import os
import textwrap
from PIL import Image
from screeninfo import get_monitors
from config import engine
from sqlalchemy.orm import sessionmaker
from models import Tweet, TwitterUser
import pygame

# --------------------------------------------------
# Database setup
# --------------------------------------------------
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

# --------------------------------------------------
# Tweet Display App
# --------------------------------------------------
class TweetDisplayApp:
    def __init__(self, username, monitor=None):
        self.username = username.strip("@")
        self.monitor = monitor
        self.screen = None
        self.tweets = []
        self.current_index = 0
        self.last_refresh = 0
        self.refresh_interval = 3600  # hourly refresh
        self.bg_colors = [
            ((58, 12, 163), (0, 212, 255)),  # purple-blue
            ((255, 0, 150), (255, 150, 0)),  # pink-orange
            ((0, 100, 255), (0, 255, 200)),  # blue-cyan
            ((255, 128, 0), (255, 0, 128))   # orange-pink
        ]
        self._init_pygame()
        self.refresh_now()

    # --------------------------------------------------
    # Initialize Pygame
    # --------------------------------------------------
    def _init_pygame(self):
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        pygame.init()
        pygame.font.init()

        if self.monitor:
            self.width = self.monitor.width
            self.height = self.monitor.height
        else:
            info = pygame.display.Info()
            self.width, self.height = info.current_w, info.current_h

        self.screen = pygame.display.set_mode((self.width, self.height), pygame.FULLSCREEN)
        pygame.display.set_caption(f"Tweet Display - @{self.username}")

    # --------------------------------------------------
    # Fetch tweets from DB
    # --------------------------------------------------
    def refresh_now(self):
        """Fetch latest tweets from the database."""
        self.last_refresh = time.time()
        user = session.query(TwitterUser).filter_by(username=self.username).first()

        if user:
            self.tweets = session.query(Tweet).filter_by(user_id=user.id).all()
            print(f"🔄 Refreshed tweets for @{self.username}: {len(self.tweets)} found.")
        else:
            self.tweets = []
            print(f"⚠️ No user found for @{self.username} in database.")

    # --------------------------------------------------
    # Draw gradient background
    # --------------------------------------------------
    def draw_gradient(self, surface, color1, color2):
        """Draw a vertical gradient on the given surface."""
        for y in range(self.height):
            r = int(color1[0] + (color2[0] - color1[0]) * (y / self.height))
            g = int(color1[1] + (color2[1] - color1[1]) * (y / self.height))
            b = int(color1[2] + (color2[2] - color1[2]) * (y / self.height))
            pygame.draw.line(surface, (r, g, b), (0, y), (self.width, y))

    # --------------------------------------------------
    # Render wrapped tweet text
    # --------------------------------------------------
    def render_tweet(self, surface, tweet_text):
        title_font = pygame.font.SysFont("arial", 60, bold=True)
        body_font = pygame.font.SysFont("arial", 42)

        # Draw username
        username_surface = title_font.render(f"@{self.username}", True, (255, 255, 255))
        username_rect = username_surface.get_rect(center=(self.width // 2, 120))
        surface.blit(username_surface, username_rect)

        # Word-wrap tweet text
        wrapped_lines = textwrap.wrap(tweet_text, width=45)
        y_offset = self.height // 2 - (len(wrapped_lines) * 30) // 2
        for line in wrapped_lines:
            tweet_surface = body_font.render(line, True, (255, 255, 255))
            tweet_rect = tweet_surface.get_rect(center=(self.width // 2, y_offset))
            surface.blit(tweet_surface, tweet_rect)
            y_offset += 55

    # --------------------------------------------------
    # Generate and draw QR Code
    # --------------------------------------------------
    def draw_qr(self, surface, tweet):
        """Generate and display QR code for this tweet."""
        tweet_url = f"https://twitter.com/{self.username}/status/{tweet.tweet_id}"
        qr = qrcode.QRCode(box_size=6, border=1)
        qr.add_data(tweet_url)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="white", back_color="black")
        qr_pil = qr_img.resize((160, 160)).convert("RGB")
        qr_surface = pygame.image.fromstring(qr_pil.tobytes(), qr_pil.size, "RGB")
        surface.blit(qr_surface, (self.width - 200, self.height - 200))

    # --------------------------------------------------
    # Smooth fade transition
    # --------------------------------------------------
    def fade_transition(self, current_surface, next_surface):
        """Smoothly fade from current_surface to next_surface."""
        fade_surface = pygame.Surface((self.width, self.height))
        for alpha in range(0, 256, 15):
            fade_surface.set_alpha(alpha)
            self.screen.blit(current_surface, (0, 0))
            fade_surface.blit(next_surface, (0, 0))
            self.screen.blit(fade_surface, (0, 0))
            pygame.display.flip()
            pygame.time.delay(30)
        self.screen.blit(next_surface, (0, 0))
        pygame.display.flip()

    # --------------------------------------------------
    # Run Display Loop
    # --------------------------------------------------
    def run(self):
        clock = pygame.time.Clock()
        gradient_index = 0

        # Initial render
        if not self.tweets:
            tweet_text = "No tweets found yet."
            tweet = None
        else:
            tweet = self.tweets[self.current_index % len(self.tweets)]
            tweet_text = tweet.text

        current_surface = pygame.Surface((self.width, self.height))
        color1, color2 = self.bg_colors[gradient_index]
        self.draw_gradient(current_surface, color1, color2)
        self.render_tweet(current_surface, tweet_text)
        if tweet:
            self.draw_qr(current_surface, tweet)
        self.screen.blit(current_surface, (0, 0))
        pygame.display.flip()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        return
                    elif event.key == pygame.K_r:
                        print("🔁 Manual refresh triggered.")
                        self.refresh_now()

            time.sleep(5)  # wait before showing next tweet
            self.current_index = (self.current_index + 1) % max(1, len(self.tweets))
            gradient_index = (gradient_index + 1) % len(self.bg_colors)

            if not self.tweets:
                tweet_text = "No tweets found yet."
                tweet = None
            else:
                tweet = self.tweets[self.current_index]
                tweet_text = tweet.text

            # Render next surface
            next_surface = pygame.Surface((self.width, self.height))
            color1, color2 = self.bg_colors[gradient_index]
            self.draw_gradient(next_surface, color1, color2)
            self.render_tweet(next_surface, tweet_text)
            if tweet:
                self.draw_qr(next_surface, tweet)

            # Transition smoothly
            self.fade_transition(current_surface, next_surface)
            current_surface = next_surface

            # Hourly refresh
            if time.time() - self.last_refresh > self.refresh_interval:
                print("⏰ Hourly refresh triggered.")
                self.refresh_now()

            clock.tick(30)

# --------------------------------------------------
# Monitor detection
# --------------------------------------------------
def detect_monitors():
    monitors = get_monitors()
    for i, m in enumerate(monitors):
        print(f"Monitor {i}: {m}")
    return monitors

# --------------------------------------------------
# Main
# --------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--username", required=True)
    args = parser.parse_args()

    monitors = detect_monitors()
    chosen_monitor = monitors[1] if len(monitors) > 1 else monitors[0]

    app = TweetDisplayApp(args.username, monitor=chosen_monitor)
    app.run()
