# test_display_window.py
import pygame
from config import SessionLocal
from models import Tweet

pygame.init()

# open a resizable windowed mode
screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("Tweet Display Test")

session = SessionLocal()
tweets = session.query(Tweet).limit(5).all()
session.close()

font_title = pygame.font.SysFont("arial", 36)
font_body = pygame.font.SysFont("arial", 24)
clock = pygame.time.Clock()

index = 0
running = True
while running:
    screen.fill((0, 0, 0))
    tweet = tweets[index]
    title = font_title.render(f"@{tweet.handle}", True, (255, 255, 255))
    body = font_body.render(tweet.text[:80], True, (200, 200, 200))
    screen.blit(title, (50, 100))
    screen.blit(body, (50, 200))

    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            # Press → or space to go next tweet
            if event.key in (pygame.K_RIGHT, pygame.K_SPACE):
                index = (index + 1) % len(tweets)
            elif event.key in (pygame.K_LEFT,):
                index = (index - 1) % len(tweets)

    clock.tick(30)

pygame.quit()
