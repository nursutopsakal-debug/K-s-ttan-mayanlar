"""
ui.py — UI components: guest cards, buttons, panels, tooltips (Dev 2)
"""
import pygame
import math
import os

# ─── Pink Wedding Color Palette ────────────────────────────────────────────────
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GOLD = (255, 210, 120)
SOFT_PINK = (255, 180, 200)
SOFT_GREEN = (120, 210, 140)
SOFT_RED = (220, 70, 70)
SOFT_YELLOW = (255, 220, 130)
DARK_BG = (60, 18, 35)
PANEL_BG = (80, 25, 45)
PANEL_BORDER = (140, 55, 80)
CARD_BG = (100, 35, 60)
CARD_BORDER = (180, 80, 110)
CARD_DRAG = (200, 90, 120)
CARD_PLACED = (70, 140, 90)
CARD_HOVER = (160, 65, 90)
TEXT_NAME = (255, 220, 230)
TEXT_TYPE = (200, 150, 170)
TEXT_DIM = (150, 100, 120)
TIMER_NORMAL = (255, 200, 210)
TIMER_WARNING = (255, 160, 80)
TIMER_DANGER = (220, 50, 50)
SCORE_GREEN = (100, 220, 130)
SCORE_RED = (220, 80, 80)

GUEST_IMG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "images", "guests")

# Guest image file mapping: g1.png through g15.png assigned to Level 1 characters
# Guest images: g1.png through g15.png — assigned by panel index
# (index-based so it works with any guest names from data files)
GUEST_IMAGE_FILES = [f"g{i}.png" for i in range(1, 16)]

CARD_WIDTH = 130
CARD_HEIGHT = 50
CARD_IMG_SIZE = 36


def load_guest_image(index, size=(CARD_IMG_SIZE, CARD_IMG_SIZE)):
    """Load and scale a guest's portrait PNG by panel index (0-based).
    Wraps around for indices >= 15 using round-robin."""
    if index < 0:
        return None
    img_index = index % len(GUEST_IMAGE_FILES)
    filename = GUEST_IMAGE_FILES[img_index]
    path = os.path.join(GUEST_IMG_DIR, filename)
    if not os.path.exists(path):
        return None
    try:
        img = pygame.image.load(path).convert_alpha()
        img = pygame.transform.scale(img, size)
        return img
    except Exception:
        return None


# ─── Guest Card ────────────────────────────────────────────────────────────────

class GuestCard:
    """A draggable guest card with pixel art portrait."""

    _image_cache = {}

    def __init__(self, guest_id: str, name: str, guest_type: str, x: int, y: int, panel_index: int = 0,
                 guest_data: dict = None):
        self.guest_id = guest_id
        self.name = name
        self.guest_type = guest_type
        self.panel_index = panel_index
        self.guest_data = guest_data or {}
        self.rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
        self.dragging = False
        self.placed_table = None
        self.placed_seat = None
        self.original_pos = (x, y)
        self.drag_offset = (0, 0)
        self.hover = False
        self._portrait = None
        self._load_portrait()

    def _load_portrait(self):
        cache_key = self.panel_index
        if cache_key in GuestCard._image_cache:
            self._portrait = GuestCard._image_cache[cache_key]
        else:
            img = load_guest_image(self.panel_index)
            GuestCard._image_cache[cache_key] = img
            self._portrait = img

    @property
    def is_placed(self):
        return self.placed_table is not None

    def draw(self, surface: pygame.Surface):
        """Draw the guest card."""
        # Choose colors based on state
        if self.dragging:
            bg = CARD_DRAG
            border = GOLD
            border_w = 2
        elif self.is_placed:
            bg = CARD_PLACED
            border = SOFT_GREEN
            border_w = 2
        elif self.hover:
            bg = CARD_HOVER
            border = SOFT_PINK
            border_w = 2
        else:
            bg = CARD_BG
            border = CARD_BORDER
            border_w = 1

        # Shadow
        if self.dragging:
            shadow = pygame.Surface((self.rect.width + 4, self.rect.height + 4), pygame.SRCALPHA)
            pygame.draw.rect(shadow, (0, 0, 0, 50), (0, 0, self.rect.width + 4, self.rect.height + 4), border_radius=8)
            surface.blit(shadow, (self.rect.x - 2, self.rect.y + 2))

        # Card background
        pygame.draw.rect(surface, bg, self.rect, border_radius=8)
        pygame.draw.rect(surface, border, self.rect, border_w, border_radius=8)

        # Portrait
        img_x = self.rect.x + 5
        img_y = self.rect.y + (CARD_HEIGHT - CARD_IMG_SIZE) // 2
        if self._portrait:
            surface.blit(self._portrait, (img_x, img_y))
            # Small border around portrait
            pygame.draw.rect(surface, border, (img_x - 1, img_y - 1, CARD_IMG_SIZE + 2, CARD_IMG_SIZE + 2), 1, border_radius=4)
        else:
            # Fallback: colored circle with initial
            cx = img_x + CARD_IMG_SIZE // 2
            cy = img_y + CARD_IMG_SIZE // 2
            pygame.draw.circle(surface, SOFT_PINK, (cx, cy), CARD_IMG_SIZE // 2 - 2)
            font_init = pygame.font.SysFont("segoeui", 16, bold=True)
            init_surf = font_init.render(self.name[0].upper(), True, DARK_BG)
            init_rect = init_surf.get_rect(center=(cx, cy))
            surface.blit(init_surf, init_rect)

        # Name text
        text_x = img_x + CARD_IMG_SIZE + 6
        font_name = pygame.font.SysFont("segoeui", 13, bold=True)
        name_surf = font_name.render(self.name, True, TEXT_NAME)
        surface.blit(name_surf, (text_x, self.rect.y + 6))

        # Type text (smaller)
        font_type = pygame.font.SysFont("segoeui", 10)
        type_surf = font_type.render(self.guest_type, True, TEXT_TYPE)
        surface.blit(type_surf, (text_x, self.rect.y + 24))

        # Placed indicator
        if self.is_placed and not self.dragging:
            check_font = pygame.font.SysFont("segoeui", 14, bold=True)
            check = check_font.render("✓", True, SOFT_GREEN)
            surface.blit(check, (self.rect.right - 16, self.rect.y + 4))

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle mouse events. Returns True if this card consumed the event."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
                self.drag_offset = (event.pos[0] - self.rect.x, event.pos[1] - self.rect.y)
                return True

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging:
                self.dragging = False
                return True

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                self.rect.x = event.pos[0] - self.drag_offset[0]
                self.rect.y = event.pos[1] - self.drag_offset[1]
                return True
            else:
                self.hover = self.rect.collidepoint(event.pos)

        return False

    def snap_to_original(self):
        """Return card to its original position in the panel."""
        self.rect.x, self.rect.y = self.original_pos
        self.placed_table = None
        self.placed_seat = None

    def snap_to_seat(self, seat_x, seat_y, table_id, seat_index):
        """Place card at a seat position."""
        self.placed_table = table_id
        self.placed_seat = seat_index
        # Center card near the seat but don't cover it completely
        self.rect.x = seat_x - CARD_WIDTH // 2
        self.rect.y = seat_y + 20


# ─── Guest Panel (sidebar) ────────────────────────────────────────────────────

class GuestPanel:
    """Side panel showing all guest cards for the current level."""

    PANEL_X = 1010
    PANEL_Y = 90
    PANEL_W = 250
    SCROLL_SPEED = 20

    def __init__(self, guests_data: list):
        """
        guests_data: list of dicts with 'id', 'name', 'type'
        """
        self.cards = []
        self.scroll_offset = 0
        self._build_cards(guests_data)

    PANEL_H = 600
    HEADER_H = 30
    CARD_PADDING = 6

    def _build_cards(self, guests_data):
        padding = self.CARD_PADDING
        y = 0  # relative to content start
        for i, g in enumerate(guests_data):
            card = GuestCard(
                guest_id=g["id"],
                name=g["name"],
                guest_type=g.get("type", "Guest"),
                x=self.PANEL_X + 10,
                y=self.PANEL_Y + self.HEADER_H + i * (CARD_HEIGHT + padding),
                panel_index=i,
                guest_data=g.get("guest_data", {})
            )
            card._list_index = i
            self.cards.append(card)
        # Total content height
        self._content_h = len(guests_data) * (CARD_HEIGHT + padding)

    def _update_card_positions(self):
        """Reposition non-dragging, non-placed cards based on scroll offset."""
        padding = self.CARD_PADDING
        for card in self.cards:
            if not card.dragging and not card.is_placed:
                base_y = self.PANEL_Y + self.HEADER_H + card._list_index * (CARD_HEIGHT + padding)
                card.rect.y = base_y - self.scroll_offset
                card.rect.x = self.PANEL_X + 10
                card.original_pos = (card.rect.x, card.rect.y)

    @property
    def _max_scroll(self):
        visible_h = self.PANEL_H - self.HEADER_H
        return max(0, self._content_h - visible_h)

    def draw(self, surface: pygame.Surface):
        panel_rect = pygame.Rect(self.PANEL_X, self.PANEL_Y, self.PANEL_W, self.PANEL_H)

        # Panel background
        bg = pygame.Surface((self.PANEL_W, self.PANEL_H), pygame.SRCALPHA)
        pygame.draw.rect(bg, (*PANEL_BG, 200), (0, 0, self.PANEL_W, self.PANEL_H), border_radius=10)
        surface.blit(bg, (self.PANEL_X, self.PANEL_Y))
        pygame.draw.rect(surface, PANEL_BORDER, panel_rect, 2, border_radius=10)

        # Title
        font_title = pygame.font.SysFont("segoeui", 15, bold=True)
        title = font_title.render("GUESTS", True, GOLD)
        title_rect = title.get_rect(center=(self.PANEL_X + self.PANEL_W // 2, self.PANEL_Y + 14))
        surface.blit(title, title_rect)

        # Count
        placed = sum(1 for c in self.cards if c.is_placed)
        count_font = pygame.font.SysFont("segoeui", 11)
        count_surf = count_font.render(f"{placed}/{len(self.cards)} seated", True, TEXT_TYPE)
        surface.blit(count_surf, (self.PANEL_X + self.PANEL_W - 85, self.PANEL_Y + 10))

        # Clip region for cards (inside panel, below header)
        clip_rect = pygame.Rect(self.PANEL_X, self.PANEL_Y + self.HEADER_H,
                                self.PANEL_W, self.PANEL_H - self.HEADER_H)
        old_clip = surface.get_clip()
        surface.set_clip(clip_rect)

        # Draw non-dragging cards (clipped)
        for card in self.cards:
            if not card.dragging:
                card.draw(surface)

        surface.set_clip(old_clip)

        # Scrollbar indicator
        if self._max_scroll > 0:
            visible_h = self.PANEL_H - self.HEADER_H
            bar_h = max(20, int(visible_h * (visible_h / self._content_h)))
            bar_y = self.PANEL_Y + self.HEADER_H + int((visible_h - bar_h) * (self.scroll_offset / self._max_scroll))
            bar_rect = pygame.Rect(self.PANEL_X + self.PANEL_W - 8, bar_y, 4, bar_h)
            pygame.draw.rect(surface, PANEL_BORDER, bar_rect, border_radius=2)

        # Draw dragging card last (on top, no clip)
        for card in self.cards:
            if card.dragging:
                card.draw(surface)

    def handle_event(self, event: pygame.event.Event) -> GuestCard | None:
        """Handle events for all cards. Returns the card that was just released (dropped), or None.
        Sets self.right_clicked_card if a card was right-clicked (for tooltip)."""
        dropped_card = None
        self.right_clicked_card = None

        # Scroll with mouse wheel inside panel
        if event.type == pygame.MOUSEWHEEL:
            panel_rect = pygame.Rect(self.PANEL_X, self.PANEL_Y, self.PANEL_W, self.PANEL_H)
            mx, my = pygame.mouse.get_pos()
            if panel_rect.collidepoint(mx, my):
                self.scroll_offset -= event.y * self.SCROLL_SPEED
                self.scroll_offset = max(0, min(self.scroll_offset, self._max_scroll))
                self._update_card_positions()
                return None

        # Right-click: show guest info
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            for card in reversed(self.cards):
                if card.rect.collidepoint(event.pos):
                    self.right_clicked_card = card
                    return None

        # Process in reverse so top card gets events first
        for card in reversed(self.cards):
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and card.dragging:
                card.handle_event(event)
                dropped_card = card
                break
            elif card.handle_event(event):
                break

        return dropped_card

    def get_unplaced_cards(self):
        return [c for c in self.cards if not c.is_placed]


# ─── Timer Display ─────────────────────────────────────────────────────────────

class TimerDisplay:
    """Countdown timer with visual warnings and penalty flash."""

    def __init__(self, seconds: int = 30):
        self.total = seconds
        self.remaining = float(seconds)
        self.penalty_flash = 0.0  # flash timer for penalty effect

    def update(self, dt: float):
        self.remaining = max(0, self.remaining - dt)
        if self.penalty_flash > 0:
            self.penalty_flash = max(0, self.penalty_flash - dt)

    def penalize(self, seconds: int = 3):
        self.remaining = max(0, self.remaining - seconds)
        self.penalty_flash = 0.5  # flash for 0.5s

    @property
    def is_expired(self) -> bool:
        return self.remaining <= 0

    def draw(self, surface: pygame.Surface):
        x, y = 20, 20
        bar_w, bar_h = 220, 24

        # Determine color
        ratio = self.remaining / self.total
        if self.penalty_flash > 0:
            color = SOFT_RED
            text_color = SOFT_RED
        elif ratio < 0.25:
            color = TIMER_DANGER
            text_color = TIMER_DANGER
        elif ratio < 0.5:
            color = TIMER_WARNING
            text_color = TIMER_WARNING
        else:
            color = SOFT_PINK
            text_color = TIMER_NORMAL

        # Background bar
        pygame.draw.rect(surface, (40, 15, 25), (x, y, bar_w, bar_h), border_radius=6)
        pygame.draw.rect(surface, PANEL_BORDER, (x, y, bar_w, bar_h), 1, border_radius=6)

        # Fill bar
        fill_w = max(0, int(bar_w * ratio))
        if fill_w > 0:
            pygame.draw.rect(surface, color, (x, y, fill_w, bar_h), border_radius=6)

        # Time text
        font = pygame.font.SysFont("segoeui", 16, bold=True)
        secs = int(self.remaining)
        ms = int((self.remaining - secs) * 10)
        time_text = f"{secs:02d}.{ms}"
        text_surf = font.render(time_text, True, text_color)
        text_rect = text_surf.get_rect(center=(x + bar_w // 2, y + bar_h // 2))
        surface.blit(text_surf, text_rect)

        # Penalty flash: "-3s" text
        if self.penalty_flash > 0:
            penalty_font = pygame.font.SysFont("segoeui", 20, bold=True)
            penalty_surf = penalty_font.render("-3s!", True, SOFT_RED)
            alpha = int(255 * (self.penalty_flash / 0.5))
            penalty_surf.set_alpha(alpha)
            surface.blit(penalty_surf, (x + bar_w + 10, y))

        # Label
        label_font = pygame.font.SysFont("segoeui", 10)
        label = label_font.render("TIME", True, TEXT_DIM)
        surface.blit(label, (x, y - 13))


# ─── Score Display ─────────────────────────────────────────────────────────────

class ScoreDisplay:
    """Simple score display in the top-right corner."""

    def __init__(self):
        self.score = 0

    def update(self, score, **kwargs):
        self.score = score

    def draw(self, surface: pygame.Surface):
        x, y = 1280 - 160, 16
        w, h = 140, 36

        # Background box
        pygame.draw.rect(surface, (40, 15, 25), (x, y, w, h), border_radius=8)
        pygame.draw.rect(surface, PANEL_BORDER, (x, y, w, h), 1, border_radius=8)

        # "SCORE" label + value
        label_font = pygame.font.SysFont("segoeui", 12, bold=True)
        value_font = pygame.font.SysFont("segoeui", 18, bold=True)

        label = label_font.render("SCORE", True, TEXT_DIM)
        surface.blit(label, (x + 10, y + 4))

        color = SCORE_GREEN if self.score >= 0 else SCORE_RED
        val = value_font.render(f"{self.score}", True, color)
        val_rect = val.get_rect(midright=(x + w - 10, y + h // 2))
        surface.blit(val, val_rect)


# ─── Button ────────────────────────────────────────────────────────────────────

class Button:
    """Simple clickable button."""

    def __init__(self, x, y, w, h, text, color=PANEL_BG, text_color=GOLD):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.hover = False

    def draw(self, surface):
        bg = self.color if not self.hover else tuple(min(255, c + 30) for c in self.color)
        pygame.draw.rect(surface, bg, self.rect, border_radius=8)
        pygame.draw.rect(surface, PANEL_BORDER, self.rect, 2, border_radius=8)

        font = pygame.font.SysFont("segoeui", 18, bold=True)
        text_surf = font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def handle_event(self, event) -> bool:
        """Returns True if button was clicked."""
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False


# ─── Guest Info Tooltip ────────────────────────────────────────────────────────

class GuestInfoTooltip:
    """Popup panel showing guest details (family, preferences, conflicts, tags)."""

    WIDTH = 280
    PADDING = 12
    LINE_H = 22
    HEADER_H = 36

    BG_COLOR = (50, 14, 30, 240)
    BORDER_COLOR = (180, 80, 110)
    HEADER_BG = (80, 25, 45)

    def __init__(self):
        self.visible = False
        self.card = None  # the GuestCard being inspected
        self.x = 0
        self.y = 0

    def show(self, card: GuestCard, mx: int, my: int, screen_w: int = 1280, screen_h: int = 720):
        """Open tooltip for the given card near the mouse position."""
        self.card = card
        self.visible = True
        self._lines = self._build_lines(card)
        h = self.HEADER_H + self.PADDING + len(self._lines) * self.LINE_H + self.PADDING
        # Position: try right of mouse, clamp to screen
        self.x = min(mx + 12, screen_w - self.WIDTH - 8)
        self.y = min(my - 10, screen_h - h - 8)
        self.x = max(4, self.x)
        self.y = max(4, self.y)
        self._height = h

    def hide(self):
        self.visible = False
        self.card = None

    def _build_lines(self, card: GuestCard):
        """Build display lines from guest_data."""
        data = card.guest_data
        lines = []

        family = data.get("family", "")
        if family:
            lines.append(("Family", family, SOFT_PINK))

        if data.get("is_vip"):
            lines.append(("Status", "★ VIP", GOLD))

        tags = data.get("tags", [])
        if tags:
            lines.append(("Tags", ", ".join(tags), TEXT_TYPE))

        preferred = data.get("preferred_with", [])
        if preferred:
            lines.append(("Likes", ", ".join(preferred), SOFT_GREEN))

        cannot = data.get("cannot_sit_with", [])
        if cannot:
            lines.append(("Conflicts", ", ".join(cannot), SOFT_RED))

        return lines

    def draw(self, surface: pygame.Surface):
        if not self.visible or not self.card:
            return

        w = self.WIDTH
        h = self._height

        # Background
        bg = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(bg, self.BG_COLOR, (0, 0, w, h), border_radius=10)
        surface.blit(bg, (self.x, self.y))
        pygame.draw.rect(surface, self.BORDER_COLOR, (self.x, self.y, w, h), 2, border_radius=10)

        # Header bar
        pygame.draw.rect(surface, self.HEADER_BG,
                         (self.x + 2, self.y + 2, w - 4, self.HEADER_H - 2), border_radius=8)

        # Guest name
        font_name = pygame.font.SysFont("segoeui", 17, bold=True)
        name_surf = font_name.render(self.card.name, True, GOLD)
        surface.blit(name_surf, (self.x + self.PADDING, self.y + 8))

        # Type badge
        font_type = pygame.font.SysFont("segoeui", 11)
        type_surf = font_type.render(self.card.guest_type, True, TEXT_TYPE)
        surface.blit(type_surf, (self.x + w - self.PADDING - type_surf.get_width(), self.y + 12))

        # Detail lines
        font_label = pygame.font.SysFont("segoeui", 12, bold=True)
        font_value = pygame.font.SysFont("segoeui", 13)
        y = self.y + self.HEADER_H + self.PADDING

        for label, value, color in self._lines:
            lbl = font_label.render(f"{label}:", True, TEXT_DIM)
            surface.blit(lbl, (self.x + self.PADDING, y))
            val = font_value.render(value, True, color)
            surface.blit(val, (self.x + self.PADDING + 80, y))
            y += self.LINE_H

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Close tooltip on any click outside it. Returns True if consumed."""
        if not self.visible:
            return False
        if event.type == pygame.MOUSEBUTTONDOWN:
            tooltip_rect = pygame.Rect(self.x, self.y, self.WIDTH, self._height)
            if not tooltip_rect.collidepoint(event.pos):
                self.hide()
        return False
