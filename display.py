# display.py
import pygame
import qrcode
import io
import threading
import time
import sys
from config import (
    SessionLocal,
    DISPLAY_FONT,
    DISPLAY_TITLE_SIZE,
    DISPLAY_BODY_SIZE,
    DISPLAY_REFRESH_INTERVAL,
)
from models import Tweet
from fetch_tweets import fetch_all_tweets


class DisplayManager:
    def __init__(self):
        pygame.init()

        # Detect available displays
        display_count = pygame.display.get_num_displays()

        if display_count > 1:
           # 🖥️ Secondary monitor detected
           print(f"Detected {display_count} displays. Using secondary monitor.")
           display_index = 1  # 0 = primary, 1 = secondary
           display_mode = pygame.display.list_modes(display=display_index)[0]
           self.screen = pygame.display.set_mode(display_mode, pygame.FULLSCREEN, display=display_index)
        else:
            # 🖥️ Only one display available
          print("Only one display detected. Using primary monitor.")
          self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

        pygame.display.set_caption("Twitter Data Analyzer")
        self.font_title = pygame.font.SysFont(DISPLAY_FONT, DISPLAY_TITLE_SIZE)
        self.font_body = pygame.font.SysFont(DISPLAY_FONT, DISPLAY_BODY_SIZE)
        self.clock = pygame.time.Clock()
        self.session = SessionLocal()
        self.current_handle = None
        self.index = 0
        self.last_refresh = time.time()

        # Background refresh thread
        self.stop_refresh = False
        self.refresh_thread = threading.Thread(target=self._refresh_scheduler, daemon=True)
        self.refresh_thread.start()

    def _refresh_scheduler(self):
        """Hourly tweet refresh in background (D6)."""
        while not self.stop_refresh:
            now = time.time()
            if now - self.last_refresh > DISPLAY_REFRESH_INTERVAL:
                print("\n🔄 Hourly refresh started...")
                try:
                    fetch_all_tweets()
                    print("✅ Hourly refresh done.")
                except Exception as e:
                    print(f"⚠️ Error during refresh: {e}")
                self.last_refresh = now
            time.sleep(60)  # Check every minute

    def _draw_text_centered(self, text, y, font, color=(255, 255, 255)):
        rendered = font.render(text, True, color)
        rect = rendered.get_rect(center=(self.screen.get_width() // 2, y))
        self.screen.blit(rendered, rect)
        return rect

    def _generate_qr_surface(self, url, size=200):
     """Generate QR code surface for the given URL."""
     qr_img = qrcode.make(url)
     buf = io.BytesIO()
     qr_img.save(buf, format="PNG")
     buf.seek(0)
     qr_surface = pygame.image.load(buf, "qr.png").convert()  # ✅ Convert to 24-bit surface
     qr_surface = pygame.transform.smoothscale(qr_surface, (size, size))
     return qr_surface


    def show_menu(self):
        """Main handle selection menu."""
        handles = sorted({t.username for t in self.session.query(Tweet).all()})
        if not handles:
            self._show_message("No tweets found. Run fetch first!", (255, 0, 0))
            time.sleep(3)
            return

        selecting = True
        while selecting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._quit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self._quit()
                    if pygame.K_1 <= event.key <= pygame.K_9:
                        idx = event.key - pygame.K_1
                        if idx < len(handles):
                            self.current_handle = handles[idx]
                            selecting = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    for i, (_, rect) in enumerate(menu_items):
                        if rect.collidepoint(x, y):
                            self.current_handle = handles[i]
                            selecting = False

            self.screen.fill((0, 0, 0))
            self._draw_text_centered("Select Twitter Handle", 100, self.font_title)
            menu_items = []
            y = 200
            for i, handle in enumerate(handles):
                rect = self._draw_text_centered(f"{i+1}. @{handle}", y, self.font_body, (0, 200, 255))
                menu_items.append((handle, rect))
                y += 80
            self._draw_text_centered("Press ESC to Exit", y + 50, self.font_body, (200, 200, 200))
            pygame.display.flip()
            self.clock.tick(30)

    def show_tweets(self):
        """Show tweets for the selected handle, with QR code."""
        tweets = self.session.query(Tweet).filter_by(username=self.current_handle).order_by(Tweet.created_at.desc()).all()
        if not tweets:
            self._show_message(f"No tweets found for @{self.current_handle}", (255, 0, 0))
            time.sleep(2)
            return

        # Create QR code for this handle
        profile_url = f"https://twitter.com/{self.current_handle}"
        qr_surface = self._generate_qr_surface(profile_url)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._quit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self._quit()
                    elif event.key == pygame.K_b:
                        return
                    elif event.key == pygame.K_RIGHT:
                        self.index = (self.index + 1) % len(tweets)
                    elif event.key == pygame.K_LEFT:
                        self.index = (self.index - 1) % len(tweets)

            self.screen.fill((20, 20, 40))
            t = tweets[self.index]
            self._draw_text_centered(f"@{t.username}", 100, self.font_title, (0, 200, 255))
            wrapped = self._wrap_text(t.content, self.font_body, self.screen.get_width() - 350)
            y = 200
            for line in wrapped:
                self._draw_text_centered(line, y, self.font_body)
                y += 60

            # Draw QR code in bottom-right
            qr_rect = qr_surface.get_rect(bottomright=(self.screen.get_width() - 50, self.screen.get_height() - 50))
            self.screen.blit(qr_surface, qr_rect)

            self._draw_text_centered("[←] Prev  [→] Next  [B] Back  [ESC] Quit", self.screen.get_height() - 100, self.font_body, (200, 200, 200))
            pygame.display.flip()
            self.clock.tick(30)

    def _wrap_text(self, text, font, max_width):
        words = text.split(" ")
        lines, current = [], ""
        for w in words:
            if font.size(current + w)[0] > max_width:
                lines.append(current)
                current = w + " "
            else:
                current += w + " "
        lines.append(current)
        return lines

    def _show_message(self, message, color=(255, 255, 255)):
        self.screen.fill((0, 0, 0))
        self._draw_text_centered(message, self.screen.get_height() // 2, self.font_body, color)
        pygame.display.flip()

    def _quit(self):
        self.stop_refresh = True
        pygame.quit()
        sys.exit()

    def run(self):
        while True:
            self.show_menu()
            if self.current_handle:
                self.show_tweets()
                self.current_handle = None


if __name__ == "__main__":
    DisplayManager().run()
