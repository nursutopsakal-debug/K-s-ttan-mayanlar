"""
renderer.py — Hall layout rendering: background, tables, zones, overlays (Dev 2)
Pink wedding theme matching the art assets (Fail1.gif style).
"""
import pygame
import math
import os

# ─── Pink Wedding Color Palette ────────────────────────────────────────────────
# Background / Floor
DARK_BG = (60, 18, 35)               # Deep wine-rose
FLOOR_COLOR = (85, 28, 50)           # Dark rosewood
FLOOR_ACCENT = (100, 35, 60)         # Slightly lighter rosewood

# Zone colors (matching Fail1.gif tones)
STAGE_COLOR = (200, 80, 100)         # Bright rose-red
VIP_COLOR = (130, 45, 70)            # Rich burgundy-pink
GENERAL_COLOR = (90, 30, 55)         # Muted dark rose
BAR_COLOR = (160, 60, 80)            # Warm cranberry
EXIT_COLOR = (80, 100, 80)           # Muted sage (contrast)
DANCE_COLOR = (170, 55, 90)          # Hot pink
SPEAKER_COLOR = (70, 25, 40)         # Dark maroon

# Zone borders & accents
ZONE_BORDER = (180, 80, 110)         # Rose border
ZONE_LABEL_BRIGHT = (255, 180, 200)  # Soft pink text

# Table
TABLE_COLOR = (140, 50, 75)          # Rose table
TABLE_BORDER = (220, 140, 170)       # Pink highlight border
TABLE_CLOTH = (160, 65, 90)          # Tablecloth shade

# Seats
SEAT_EMPTY = (110, 40, 65)           # Empty seat (dark rose)
SEAT_FILLED = (100, 200, 130)        # Green for placed guest
SEAT_HOVER = (255, 220, 150)         # Warm gold hover
SEAT_BAD = (220, 50, 60)             # Red error

# Text
WHITE = (255, 255, 255)
GOLD = (255, 210, 120)               # Warm wedding gold
SOFT_WHITE = (255, 220, 230)         # Pinkish white
TEXT_DIM = (180, 120, 140)           # Muted pink text
ROSE_TEXT = (255, 160, 180)          # Rose text for labels

# Decorative
LIGHT_GLOW = (255, 200, 180)        # Fairy light glow
FLOWER_PINK = (220, 80, 110)        # Flower accent
FLOWER_DARK = (150, 40, 65)         # Flower shadow

SCREEN_W, SCREEN_H = 1280, 720

# ─── Asset Paths ───────────────────────────────────────────────────────────────
ASSET_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "images", "hall")

# ─── Hall Zones ────────────────────────────────────────────────────────────────
ZONES = {
    "stage":          {"rect": pygame.Rect(440, 10, 400, 70),  "color": STAGE_COLOR,   "label": "✦ STAGE ✦",    "icon": "♥"},
    "speakers_left":  {"rect": pygame.Rect(350, 15, 80, 50),   "color": SPEAKER_COLOR, "label": "♪",            "icon": None},
    "speakers_right": {"rect": pygame.Rect(850, 15, 80, 50),   "color": SPEAKER_COLOR, "label": "♪",            "icon": None},
    "vip_bride":      {"rect": pygame.Rect(200, 100, 380, 160),"color": VIP_COLOR,     "label": "BRIDE VIP",    "icon": "♥"},
    "vip_groom":      {"rect": pygame.Rect(700, 100, 380, 160),"color": VIP_COLOR,     "label": "GROOM VIP",    "icon": "♥"},
    "general":        {"rect": pygame.Rect(40, 280, 1200, 280),"color": GENERAL_COLOR, "label": "",             "icon": None},
    "bar":            {"rect": pygame.Rect(1100, 580, 160, 110),"color": BAR_COLOR,    "label": "BAR 🍷",       "icon": None},
    "exit":           {"rect": pygame.Rect(20, 580, 160, 110), "color": EXIT_COLOR,    "label": "EXIT →",       "icon": None},
    "dance_floor":    {"rect": pygame.Rect(500, 590, 280, 100),"color": DANCE_COLOR,   "label": "DANCE FLOOR 💃","icon": None},
}

# ─── Table Layouts Per Level ───────────────────────────────────────────────────
LEVEL_TABLE_LAYOUTS = {
    1: [  # 3 tables
        (300, 190, "vip_bride"),
        (700, 190, "vip_groom"),
        (500, 400, "general"),
    ],
    2: [  # 5 tables
        (250, 180, "vip_bride"),
        (700, 180, "vip_groom"),
        (150, 400, "general"),
        (475, 400, "general"),
        (800, 400, "general"),
    ],
    3: [  # 7 tables — all x < 960 to stay clear of guest panel
        (250, 170, "vip_bride"),
        (650, 170, "vip_groom"),
        (120, 360, "general"),
        (370, 360, "general"),
        (620, 360, "general"),
        (870, 360, "general"),
        (490, 530, "general"),
    ],
}


# ─── Decorative Helpers ────────────────────────────────────────────────────────

def _draw_fairy_lights(surface, y=8, count=20):
    """Draw a string of fairy lights across the top."""
    spacing = SCREEN_W // (count + 1)
    for i in range(count):
        x = spacing * (i + 1)
        # Wire
        if i < count - 1:
            nx = spacing * (i + 2)
            pygame.draw.line(surface, (120, 60, 80), (x, y), (nx, y + 3), 1)
        # Glow
        glow = pygame.Surface((18, 18), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*LIGHT_GLOW, 40), (9, 9), 9)
        surface.blit(glow, (x - 9, y - 5))
        # Bulb
        color = GOLD if i % 3 == 0 else LIGHT_GLOW if i % 3 == 1 else FLOWER_PINK
        pygame.draw.circle(surface, color, (x, y + 2), 4)


def _draw_flower_vase(surface, x, y):
    """Draw a small decorative flower arrangement."""
    # Vase
    pygame.draw.ellipse(surface, (180, 130, 150), (x - 8, y, 16, 12))
    pygame.draw.rect(surface, (160, 110, 130), (x - 5, y - 4, 10, 8), border_radius=2)
    # Flowers
    for angle_offset in [-0.8, 0, 0.8]:
        fx = x + int(10 * math.sin(angle_offset))
        fy = y - 10 + int(-4 * abs(math.sin(angle_offset)))
        pygame.draw.circle(surface, FLOWER_PINK, (fx, fy), 5)
        pygame.draw.circle(surface, GOLD, (fx, fy), 2)


# ─── Table Renderer ───────────────────────────────────────────────────────────

class TableRenderer:
    """Draws a single round table with seats arranged in a circle."""

    TABLE_RADIUS = 48
    SEAT_RADIUS = 15
    SEAT_DISTANCE = 74

    @staticmethod
    def draw(surface, x, y, table_id, seats=5, seated_guests=None, highlight_seats=None):
        if seated_guests is None:
            seated_guests = [None] * seats
        if highlight_seats is None:
            highlight_seats = {}

        # Table shadow
        shadow = pygame.Surface((TableRenderer.TABLE_RADIUS * 2 + 10, TableRenderer.TABLE_RADIUS * 2 + 10), pygame.SRCALPHA)
        pygame.draw.circle(shadow, (0, 0, 0, 35), (TableRenderer.TABLE_RADIUS + 5, TableRenderer.TABLE_RADIUS + 5), TableRenderer.TABLE_RADIUS + 3)
        surface.blit(shadow, (x - TableRenderer.TABLE_RADIUS - 5, y - TableRenderer.TABLE_RADIUS - 2))

        # Table cloth (outer ring)
        pygame.draw.circle(surface, TABLE_CLOTH, (x, y), TableRenderer.TABLE_RADIUS + 3)
        # Table top
        pygame.draw.circle(surface, TABLE_COLOR, (x, y), TableRenderer.TABLE_RADIUS)
        # Inner decorative ring
        pygame.draw.circle(surface, TABLE_BORDER, (x, y), TableRenderer.TABLE_RADIUS, 2)
        pygame.draw.circle(surface, (200, 100, 130), (x, y), TableRenderer.TABLE_RADIUS - 8, 1)

        # Center decoration (small flower)
        pygame.draw.circle(surface, FLOWER_PINK, (x, y - 6), 4)
        pygame.draw.circle(surface, GOLD, (x, y - 6), 2)

        # Table number
        font_sm = pygame.font.SysFont("segoeui", 15, bold=True)
        label = font_sm.render(f"T{table_id + 1}", True, GOLD)
        label_rect = label.get_rect(center=(x, y + 8))
        surface.blit(label, label_rect)

        # Seats
        seat_positions = []
        for i in range(seats):
            angle = (2 * math.pi / seats) * i - math.pi / 2
            sx = x + int(TableRenderer.SEAT_DISTANCE * math.cos(angle))
            sy = y + int(TableRenderer.SEAT_DISTANCE * math.sin(angle))
            seat_positions.append((sx, sy))

            # Determine seat color
            if i in highlight_seats:
                color_map = {"green": SEAT_FILLED, "red": SEAT_BAD, "yellow": SEAT_HOVER}
                color = color_map.get(highlight_seats[i], SEAT_EMPTY)
            elif seated_guests[i] is not None:
                color = SEAT_FILLED
            else:
                color = SEAT_EMPTY

            # Seat shadow
            pygame.draw.circle(surface, (0, 0, 0, 30) if len(color) == 3 else color, (sx + 1, sy + 2), TableRenderer.SEAT_RADIUS)
            # Seat body
            pygame.draw.circle(surface, color, (sx, sy), TableRenderer.SEAT_RADIUS)
            # Seat border — brighter for filled
            border_color = (255, 200, 210) if seated_guests[i] else TABLE_BORDER
            pygame.draw.circle(surface, border_color, (sx, sy), TableRenderer.SEAT_RADIUS, 2)

            # Guest name or seat number
            if seated_guests[i] is not None:
                name = seated_guests[i]
                # Initial inside seat circle
                init_font = pygame.font.SysFont("segoeui", 13, bold=True)
                init_surf = init_font.render(name[0].upper(), True, WHITE)
                init_rect = init_surf.get_rect(center=(sx, sy))
                surface.blit(init_surf, init_rect)

                # Full name label below the seat
                name_font = pygame.font.SysFont("segoeui", 10, bold=True)
                # Truncate long names
                display_name = name if len(name) <= 12 else name[:11] + "…"
                name_surf = name_font.render(display_name, True, SOFT_WHITE)
                # Background pill for readability
                nw, nh = name_surf.get_size()
                pill = pygame.Surface((nw + 6, nh + 2), pygame.SRCALPHA)
                pygame.draw.rect(pill, (40, 15, 30, 180), (0, 0, nw + 6, nh + 2), border_radius=4)
                pill_rect = pill.get_rect(center=(sx, sy + TableRenderer.SEAT_RADIUS + 10))
                surface.blit(pill, pill_rect)
                name_rect = name_surf.get_rect(center=(sx, sy + TableRenderer.SEAT_RADIUS + 10))
                surface.blit(name_surf, name_rect)
            else:
                num_font = pygame.font.SysFont("segoeui", 10)
                num_surf = num_font.render(str(i + 1), True, TEXT_DIM)
                num_rect = num_surf.get_rect(center=(sx, sy))
                surface.blit(num_surf, num_rect)

        return seat_positions


# ─── Screen Image Loader ──────────────────────────────────────────────────────

class ScreenImages:
    """Loads and caches screen images (start, win, fail). Supports animated GIFs via Pillow."""

    def __init__(self):
        self._cache = {}
        self._gif_frames = {}   # filename -> list of (surface, duration_ms)
        self._gif_index = {}    # filename -> current frame index
        self._gif_timer = {}    # filename -> elapsed ms

    def _load(self, filename, size=(SCREEN_W, SCREEN_H)):
        if filename in self._cache:
            return self._cache[filename]
        path = os.path.join(ASSET_DIR, filename)
        if not os.path.exists(path):
            return None
        try:
            img = pygame.image.load(path).convert()
            img = pygame.transform.scale(img, size)
            self._cache[filename] = img
            return img
        except Exception:
            return None

    def _load_gif_frames(self, filename, size=(SCREEN_W, SCREEN_H)):
        """Extract all frames from an animated GIF using Pillow."""
        if filename in self._gif_frames:
            return self._gif_frames[filename]
        path = os.path.join(ASSET_DIR, filename)
        if not os.path.exists(path):
            return None
        try:
            from PIL import Image
            pil_img = Image.open(path)
            frames = []
            try:
                while True:
                    frame = pil_img.convert("RGBA")
                    frame = frame.resize(size, Image.LANCZOS)
                    raw = frame.tobytes()
                    surf = pygame.image.fromstring(raw, size, "RGBA").convert_alpha()
                    duration = pil_img.info.get("duration", 100)
                    frames.append((surf, max(duration, 30)))
                    pil_img.seek(pil_img.tell() + 1)
            except EOFError:
                pass
            if frames:
                self._gif_frames[filename] = frames
                self._gif_index[filename] = 0
                self._gif_timer[filename] = 0.0
                return frames
        except Exception:
            pass
        # Fallback: load as static image
        static = self._load(filename, size)
        if static:
            self._gif_frames[filename] = [(static, 100)]
            self._gif_index[filename] = 0
            self._gif_timer[filename] = 0.0
            return self._gif_frames[filename]
        return None

    def get_gif_frame(self, filename, dt_ms=0):
        """Get current frame of an animated GIF, advancing by dt_ms."""
        frames = self._gif_frames.get(filename)
        if not frames:
            frames = self._load_gif_frames(filename)
        if not frames:
            return None
        idx = self._gif_index.get(filename, 0)
        self._gif_timer[filename] = self._gif_timer.get(filename, 0) + dt_ms
        _, duration = frames[idx]
        while self._gif_timer[filename] >= duration:
            self._gif_timer[filename] -= duration
            idx = (idx + 1) % len(frames)
            _, duration = frames[idx]
        self._gif_index[filename] = idx
        return frames[idx][0]

    @property
    def start_screen(self):
        return self._load("startScreen.jpg")

    @property
    def good_end_screen(self):
        return self._load("goodEndScreen.jpg")

    @property
    def fail1_screen(self):
        return self._load("Fail1.gif")

    @property
    def fail2_screen(self):
        return self._load("Fail2.gif")


# ─── Hall Renderer ────────────────────────────────────────────────────────────

class HallRenderer:
    """Draws the wedding hall background, zones, and tables."""

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.images = ScreenImages()

    def draw_background(self):
        """Draw the pink wedding hall floor with decorative elements."""
        self.screen.fill(DARK_BG)

        # Main floor area — gradient-like with two rects
        floor_outer = pygame.Rect(8, 4, 1264, 712)
        floor_inner = pygame.Rect(15, 10, 1250, 700)
        pygame.draw.rect(self.screen, FLOOR_ACCENT, floor_outer, border_radius=14)
        pygame.draw.rect(self.screen, FLOOR_COLOR, floor_inner, border_radius=10)

        # Decorative border (double line)
        pygame.draw.rect(self.screen, ZONE_BORDER, floor_outer, 2, border_radius=14)
        pygame.draw.rect(self.screen, (120, 50, 70), floor_inner, 1, border_radius=10)

        # Fairy lights along the top
        _draw_fairy_lights(self.screen, y=25, count=22)

        # Corner flower vases
        _draw_flower_vase(self.screen, 50, 40)
        _draw_flower_vase(self.screen, 1230, 40)
        _draw_flower_vase(self.screen, 50, 680)
        _draw_flower_vase(self.screen, 1230, 680)

        # Floor pattern — subtle diamond grid
        for gx in range(0, SCREEN_W, 80):
            for gy in range(0, SCREEN_H, 80):
                pygame.draw.line(self.screen, (95, 32, 55), (gx, gy), (gx + 40, gy + 40), 1)
                pygame.draw.line(self.screen, (95, 32, 55), (gx + 80, gy), (gx + 40, gy + 40), 1)

    def draw_zones(self):
        """Draw labeled zone areas with pink theme."""
        font = pygame.font.SysFont("segoeui", 14, bold=True)

        for zone_name, zone_info in ZONES.items():
            rect = zone_info["rect"]
            color = zone_info["color"]
            label_text = zone_info["label"]

            # Zone background with rounded transparency
            s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            pygame.draw.rect(s, (*color, 55), (0, 0, rect.width, rect.height), border_radius=6)
            self.screen.blit(s, rect.topleft)

            # Zone border
            pygame.draw.rect(self.screen, (*color,), rect, 1, border_radius=6)

            # Zone label
            if label_text:
                bright = tuple(min(255, c + 100) for c in color[:3])
                label = font.render(label_text, True, bright)
                label_rect = label.get_rect(center=rect.center)
                self.screen.blit(label, label_rect)

    def draw_tables(self, level, tables_data=None):
        """
        Draw all tables for a given level.
        Returns: list of (table_id, x, y, seat_positions) for hit detection.
        """
        layout = LEVEL_TABLE_LAYOUTS.get(level, LEVEL_TABLE_LAYOUTS[1])
        result = []

        for i, (tx, ty, zone) in enumerate(layout):
            seated = None
            highlights = None
            if tables_data and i < len(tables_data):
                seated = tables_data[i].get("seated_guests")
                highlights = tables_data[i].get("highlight_seats")

            seat_positions = TableRenderer.draw(
                self.screen, tx, ty, i, seats=5,
                seated_guests=seated, highlight_seats=highlights
            )
            result.append((i, tx, ty, seat_positions))

        return result

    def draw_fade_overlay(self, alpha=0):
        """Draw a black overlay for fade-to-black effect."""
        if alpha > 0:
            overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, min(255, int(alpha))))
            self.screen.blit(overlay, (0, 0))

    def draw_screen_image(self, image_name):
        """
        Draw a full-screen image.
        image_name: 'start', 'good_end', 'fail1', 'fail2'
        """
        img_map = {
            "start": self.images.start_screen,
            "good_end": self.images.good_end_screen,
            "fail1": self.images.fail1_screen,
            "fail2": self.images.fail2_screen,
        }
        img = img_map.get(image_name)
        if img:
            self.screen.blit(img, (0, 0))
            return True
        return False

