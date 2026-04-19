"""
ui.py — UI components: guest cards, buttons, panels, tooltips (Dev 2)
"""
import pygame


# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GOLD = (212, 175, 55)
SOFT_PINK = (255, 200, 200)
SOFT_GREEN = (200, 255, 200)
SOFT_RED = (255, 120, 120)
SOFT_YELLOW = (255, 255, 150)
DARK_BG = (30, 20, 40)
PANEL_BG = (45, 35, 60)
TABLE_COLOR = (80, 60, 100)
TIMER_RED = (220, 50, 50)
TIMER_NORMAL = (255, 255, 255)


class GuestCard:
    """A draggable guest card."""

    def __init__(self, guest_id: str, name: str, guest_type: str, x: int, y: int):
        self.guest_id = guest_id
        self.name = name
        self.guest_type = guest_type
        self.rect = pygame.Rect(x, y, 120, 40)
        self.dragging = False
        self.placed_table = None
        self.placed_seat = None
        self.original_pos = (x, y)

    def draw(self, surface: pygame.Surface, font: pygame.font.Font):
        pass

    def handle_event(self, event: pygame.event.Event):
        pass


class TableWidget:
    """A table rendered as a circle with seat slots."""

    def __init__(self, table_id: int, x: int, y: int, seats: int = 5):
        self.table_id = table_id
        self.x = x
        self.y = y
        self.seats = seats
        self.seated_guests = [None] * seats
        self.highlight = None  # None, 'green', 'red', 'yellow'

    def draw(self, surface: pygame.Surface, font: pygame.font.Font):
        pass

    def get_nearest_seat(self, pos: tuple) -> int | None:
        pass


class TimerDisplay:
    """Countdown timer with visual warnings."""

    def __init__(self, seconds: int = 30):
        self.total = seconds
        self.remaining = float(seconds)

    def update(self, dt: float):
        self.remaining = max(0, self.remaining - dt)

    def penalize(self, seconds: int = 3):
        self.remaining = max(0, self.remaining - seconds)

    @property
    def is_expired(self) -> bool:
        return self.remaining <= 0

    def draw(self, surface: pygame.Surface, font: pygame.font.Font):
        pass
