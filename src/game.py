"""
game.py — Main game loop and screen state management (Dev 2)

Screens:
  - MENU: Title screen
  - LEVEL_INTRO: Show guest list and rules before each level
  - GAMEPLAY: Active drag-and-drop seating
  - LEVEL_RESULT: Score breakdown after level
  - WIN: Final win screen
  - LOSE: Crying bride animation
"""
import pygame
from enum import Enum, auto


class GameScreen(Enum):
    MENU = auto()
    LEVEL_INTRO = auto()
    GAMEPLAY = auto()
    LEVEL_RESULT = auto()
    WIN = auto()
    LOSE = auto()


class Game:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.current_screen = GameScreen.MENU
        self.current_level = 1
        self.max_levels = 3

    def handle_event(self, event: pygame.event.Event):
        """Route events to the active screen handler."""
        pass

    def update(self, dt: float):
        """Update logic for the active screen."""
        pass

    def render(self):
        """Render the active screen."""
        pass
