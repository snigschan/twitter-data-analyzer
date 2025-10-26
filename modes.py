# File: modes.py
"""
Small UI helpers.
"""
import pygame
from typing import List

def split_text_to_lines(text: str, font: pygame.font.Font, max_width: int) -> List[str]:
    words = text.split()
    lines = []
    cur = ""
    for w in words:
        test = cur + (" " if cur else "") + w
        if font.size(test)[0] <= max_width:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines
