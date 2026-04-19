"""
game.py — Main game loop and screen state management (Dev 2)

Screens:
  - MENU: Title screen (startScreen.jpg)
  - LEVEL_INTRO: Show guest list and rules before each level
  - GAMEPLAY: Active drag-and-drop seating
  - LEVEL_RESULT: Score breakdown after level
  - WIN: Final win screen (goodEndScreen.jpg)
  - LOSE: Crying bride animation (Fail1.gif → Fail2.gif)
"""
import pygame
import math
import json
import os
from enum import Enum, auto

from src.renderer import HallRenderer, LEVEL_TABLE_LAYOUTS, SCREEN_W, SCREEN_H
from src.ui import (
    GuestPanel, GuestCard, TimerDisplay, ScoreDisplay, Button,
    GOLD, SOFT_PINK, SOFT_GREEN, SOFT_RED, DARK_BG, PANEL_BG, PANEL_BORDER,
    TEXT_NAME, TEXT_TYPE, TEXT_DIM, WHITE, BLACK, CARD_WIDTH, CARD_HEIGHT
)

# ─── Constants ─────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
LEVEL_TIME = 30  # seconds per level
PENALTY_SECONDS = 3

# ─── Helpers ───────────────────────────────────────────────────────────────────

def _load_json(filename):
    path = os.path.join(DATA_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _tag_to_type(tags):
    """Convert Dev1 tags list to a short display string."""
    mapping = {
        "social": "Social",
        "funny": "Entertainer",
        "quiet": "Quiet",
        "family_oriented": "Family",
        "dramatic": "Dramatic",
        "rival": "Rival",
        "ex_partner": "Ex-Partner",
    }
    for t in tags:
        if t in mapping:
            return mapping[t]
    return "Guest"


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
        self.hall = HallRenderer(screen)
        self.current_screen = GameScreen.MENU
        self.current_level = 1
        self.max_levels = 3

        # Data
        self.all_guests = _load_json("guests.json")
        self.all_levels = _load_json("levels.json")

        # Gameplay state (initialized per level)
        self.panel = None
        self.timer = None
        self.score_display = None
        self.table_seats = {}      # (table_id, seat_idx) -> guest_name
        self.table_info = []       # list returned by draw_tables for hit-detection
        self.level_scores = None   # result from scoring after level ends

        # Level result
        self.level_total_scores = []  # accumulated scores per level

        # Lose screen state
        self._lose_fade_alpha = 0
        self._lose_phase = 0       # 0=fade, 1=fail1, 2=fail2
        self._lose_timer = 0.0

        # UI elements
        self._btn_start = Button(SCREEN_W // 2 - 100, 520, 200, 50, "PLAY", (140, 45, 70), GOLD)
        self._btn_next = Button(SCREEN_W // 2 - 100, 580, 200, 50, "NEXT LEVEL", (140, 45, 70), GOLD)
        self._btn_retry = Button(SCREEN_W // 2 - 100, 580, 200, 50, "TRY AGAIN", (140, 45, 70), GOLD)
        self._btn_intro_start = Button(SCREEN_W // 2 - 100, 640, 200, 50, "START", (140, 45, 70), GOLD)
        self._btn_menu = Button(SCREEN_W // 2 - 100, 580, 200, 50, "MAIN MENU", (140, 45, 70), GOLD)

    # ─── Level Setup ───────────────────────────────────────────────────────

    def _start_level(self):
        """Initialize gameplay state for the current level."""
        level_key = f"level_{self.current_level}"
        guests_raw = self.all_guests.get(level_key, [])

        # Build guest dicts for GuestPanel
        guests_for_panel = []
        for i, g in enumerate(guests_raw):
            gid = g["name"].lower().replace(" ", "_").replace(".", "")
            guests_for_panel.append({
                "id": gid,
                "name": g["name"],
                "type": _tag_to_type(g.get("tags", [])),
            })

        self.panel = GuestPanel(guests_for_panel)
        self.timer = TimerDisplay(LEVEL_TIME)
        self.score_display = ScoreDisplay()
        self.table_seats = {}
        self.table_info = []
        self.level_scores = None
        self.current_screen = GameScreen.GAMEPLAY

    def _get_level_data(self):
        level_key = f"level_{self.current_level}"
        return self.all_levels.get(level_key, {})

    def _get_guests_data(self):
        level_key = f"level_{self.current_level}"
        return self.all_guests.get(level_key, [])

    def _build_player_layout(self):
        """Convert table_seats dict to the format scoring.py expects."""
        level_data = self._get_level_data()
        table_count = level_data.get("table_count", 3)
        layout = {}
        for tid in range(table_count):
            table_name = f"Table {tid + 1}"
            guests_at_table = []
            for si in range(5):
                gname = self.table_seats.get((tid, si))
                if gname:
                    guests_at_table.append(gname)
            layout[table_name] = guests_at_table
        return layout

    def _evaluate_layout(self):
        """Call scoring engine and return results."""
        try:
            from src.scoring import evaluate
            layout = self._build_player_layout()
            level_data = self._get_level_data()
            guests_data = self._get_guests_data()
            return evaluate(layout, level_data, guests_data)
        except Exception:
            # Fallback if scoring not available
            return {"total_score": 0, "happiness": 0, "tension": 0,
                    "entertainment": 0, "family_balance": 0, "vip_satisfaction": 0,
                    "hidden_bonuses": 0, "gossip": 0, "major_crisis": 0,
                    "penalties": [], "has_major_violation": False}

    def _check_violations_on_drop(self, guest_name, table_id):
        """Check if dropping a guest causes a hard constraint violation → penalty."""
        guests_data = self._get_guests_data()
        guests_dict = {g["name"]: g for g in guests_data}
        guest = guests_dict.get(guest_name)
        if not guest:
            return False

        cannot = guest.get("cannot_sit_with", [])
        # Check existing guests at this table
        for si in range(5):
            other = self.table_seats.get((table_id, si))
            if other and other in cannot:
                return True
            # Also check the other direction
            other_guest = guests_dict.get(other)
            if other_guest and guest_name in other_guest.get("cannot_sit_with", []):
                return True
        return False

    # ─── Event Handling ────────────────────────────────────────────────────

    def handle_event(self, event: pygame.event.Event):
        if self.current_screen == GameScreen.MENU:
            self._handle_menu_event(event)
        elif self.current_screen == GameScreen.LEVEL_INTRO:
            self._handle_intro_event(event)
        elif self.current_screen == GameScreen.GAMEPLAY:
            self._handle_gameplay_event(event)
        elif self.current_screen == GameScreen.LEVEL_RESULT:
            self._handle_result_event(event)
        elif self.current_screen == GameScreen.WIN:
            self._handle_win_event(event)
        elif self.current_screen == GameScreen.LOSE:
            self._handle_lose_event(event)

    def _handle_menu_event(self, event):
        if self._btn_start.handle_event(event):
            self.current_level = 1
            self.level_total_scores = []
            self.current_screen = GameScreen.LEVEL_INTRO

    def _handle_intro_event(self, event):
        if self._btn_intro_start.handle_event(event):
            self._start_level()

    def _handle_gameplay_event(self, event):
        if not self.panel or not self.timer:
            return
        dropped = self.panel.handle_event(event)
        if dropped:
            self._process_drop(dropped)

    def _process_drop(self, dropped: GuestCard):
        """Try to seat a dropped card at the nearest empty seat."""
        placed = False
        layout = LEVEL_TABLE_LAYOUTS.get(self.current_level, LEVEL_TABLE_LAYOUTS[1])

        for tid, (tx, ty, zone) in enumerate(layout):
            for si in range(5):
                angle = (2 * math.pi / 5) * si - math.pi / 2
                sx = tx + int(74 * math.cos(angle))
                sy = ty + int(74 * math.sin(angle))
                dist = math.sqrt((dropped.rect.centerx - sx) ** 2 + (dropped.rect.centery - sy) ** 2)
                if dist < 30 and (tid, si) not in self.table_seats:
                    # Check for violations
                    has_violation = self._check_violations_on_drop(dropped.name, tid)

                    dropped.snap_to_seat(sx, sy, tid, si)
                    self.table_seats[(tid, si)] = dropped.name
                    placed = True

                    if has_violation and self.timer:
                        self.timer.penalize(PENALTY_SECONDS)

                    # Update score
                    self._update_score()
                    break
            if placed:
                break

        if not placed:
            # If was previously placed, remove from table
            if dropped.placed_table is not None:
                self.table_seats.pop((dropped.placed_table, dropped.placed_seat), None)
            dropped.snap_to_original()
            self._update_score()

    def _update_score(self):
        """Recalculate score based on current layout."""
        scores = self._evaluate_layout()
        if self.score_display:
            self.score_display.update(int(scores.get("total_score", 0)))

    def _handle_result_event(self, event):
        if self.current_level < self.max_levels:
            if self._btn_next.handle_event(event):
                self.current_level += 1
                self.current_screen = GameScreen.LEVEL_INTRO
        else:
            if self._btn_next.handle_event(event):
                self.current_screen = GameScreen.WIN

    def _handle_win_event(self, event):
        if self._btn_menu.handle_event(event):
            self.current_screen = GameScreen.MENU

    def _handle_lose_event(self, event):
        if self._lose_phase >= 2:
            if self._btn_retry.handle_event(event):
                self._lose_phase = 0
                self._lose_fade_alpha = 0
                self._lose_timer = 0
                self.current_screen = GameScreen.LEVEL_INTRO

    # ─── Update ────────────────────────────────────────────────────────────

    def update(self, dt: float):
        if self.current_screen == GameScreen.GAMEPLAY:
            self._update_gameplay(dt)
        elif self.current_screen == GameScreen.LOSE:
            self._update_lose(dt)

    def _update_gameplay(self, dt):
        if self.timer:
            self.timer.update(dt)
            if self.timer.is_expired:
                # Time's up → check if all seated
                all_placed = self.panel and all(c.is_placed for c in self.panel.cards)
                if all_placed:
                    self._finish_level()
                else:
                    self._start_lose()

        # Also check if all guests seated (auto-finish)
        if self.panel and all(c.is_placed for c in self.panel.cards):
            self._finish_level()

    def _finish_level(self):
        """Level completed successfully."""
        self.level_scores = self._evaluate_layout()
        self.level_total_scores.append(self.level_scores.get("total_score", 0))
        self.current_screen = GameScreen.LEVEL_RESULT

    def _start_lose(self):
        """Transition to lose screen."""
        self._lose_fade_alpha = 0
        self._lose_phase = 0
        self._lose_timer = 0
        self.current_screen = GameScreen.LOSE

    def _update_lose(self, dt):
        self._lose_timer += dt
        if self._lose_phase == 0:
            # Fade to black over 2 seconds
            self._lose_fade_alpha = min(255, self._lose_fade_alpha + dt * 128)
            if self._lose_fade_alpha >= 255:
                self._lose_phase = 1
                self._lose_timer = 0
        elif self._lose_phase == 1:
            # Show Fail1 for 3 seconds
            if self._lose_timer > 3.0:
                self._lose_phase = 2
                self._lose_timer = 0

    # ─── Render ────────────────────────────────────────────────────────────

    def render(self):
        if self.current_screen == GameScreen.MENU:
            self._render_menu()
        elif self.current_screen == GameScreen.LEVEL_INTRO:
            self._render_intro()
        elif self.current_screen == GameScreen.GAMEPLAY:
            self._render_gameplay()
        elif self.current_screen == GameScreen.LEVEL_RESULT:
            self._render_result()
        elif self.current_screen == GameScreen.WIN:
            self._render_win()
        elif self.current_screen == GameScreen.LOSE:
            self._render_lose()

    # ─── Menu Screen ──────────────────────────────────────────────────────

    def _render_menu(self):
        # Try to show start screen image
        if not self.hall.draw_screen_image("start"):
            self.screen.fill(DARK_BG)

        # Semi-transparent dark overlay for readability
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        self.screen.blit(overlay, (0, 0))

        # Title — black with gold outline effect
        font_big = pygame.font.SysFont("segoeui", 48, bold=True)
        title = font_big.render("Seat the Drama", True, BLACK)
        title_rect = title.get_rect(center=(SCREEN_W // 2, 200))
        self.screen.blit(title, title_rect)

        # Subtitle
        font_sub = pygame.font.SysFont("segoeui", 20)
        sub = font_sub.render("Arrange the guests. Prevent the chaos. Save the wedding.", True, BLACK)
        sub_rect = sub.get_rect(center=(SCREEN_W // 2, 260))
        self.screen.blit(sub, sub_rect)

        # Hearts decoration
        font_heart = pygame.font.SysFont("segoeui", 28)
        hearts = font_heart.render("♥  ♥  ♥", True, (180, 30, 60))
        hearts_rect = hearts.get_rect(center=(SCREEN_W // 2, 310))
        self.screen.blit(hearts, hearts_rect)

        # Instructions — black text
        font_instr = pygame.font.SysFont("segoeui", 14)
        instructions = [
            "Drag guests from the panel to table seats",
            "Avoid seating enemies together (-3s penalty!)",
            "Seat all guests before time runs out",
        ]
        for i, line in enumerate(instructions):
            surf = font_instr.render(line, True, BLACK)
            rect = surf.get_rect(center=(SCREEN_W // 2, 380 + i * 28))
            self.screen.blit(surf, rect)

        # Play button
        self._btn_start.rect.center = (SCREEN_W // 2, 500)
        self._btn_start.draw(self.screen)

    # ─── Level Intro Screen ──────────────────────────────────────────────

    def _render_intro(self):
        self.screen.fill(DARK_BG)

        level_data = self._get_level_data()
        guests_raw = self._get_guests_data()

        # Level title
        font_big = pygame.font.SysFont("segoeui", 40, bold=True)
        title = font_big.render(f"Level {self.current_level}", True, GOLD)
        title_rect = title.get_rect(center=(SCREEN_W // 2, 55))
        self.screen.blit(title, title_rect)

        # Level name
        font_name = pygame.font.SysFont("segoeui", 22, bold=True)
        name_text = level_data.get("level_name", "")
        name_surf = font_name.render(name_text, True, SOFT_PINK)
        name_rect = name_surf.get_rect(center=(SCREEN_W // 2, 100))
        self.screen.blit(name_surf, name_rect)

        # Info bar
        font_info = pygame.font.SysFont("segoeui", 16, bold=True)
        tables = level_data.get("table_count", 3)
        info_text = f"Tables: {tables}   |   Guests: {len(guests_raw)}   |   Seats per table: 5   |   Time: {LEVEL_TIME}s"
        info_surf = font_info.render(info_text, True, GOLD)
        info_rect = info_surf.get_rect(center=(SCREEN_W // 2, 145))
        self.screen.blit(info_surf, info_rect)

        # Divider
        pygame.draw.line(self.screen, PANEL_BORDER, (200, 175), (SCREEN_W - 200, 175), 1)

        # HOW TO PLAY section
        font_section = pygame.font.SysFont("segoeui", 24, bold=True)
        how_title = font_section.render("How to Play", True, GOLD)
        how_rect = how_title.get_rect(center=(SCREEN_W // 2, 210))
        self.screen.blit(how_title, how_rect)

        font_rule = pygame.font.SysFont("segoeui", 16)
        instructions = [
            "Drag guest cards from the right panel and drop them onto table seats.",
            "Each guest has preferences and conflicts — read their types carefully!",
            "Seating enemies at the same table causes a 3-second time penalty.",
            "VIP guests should be placed at prominent, visible tables.",
            "Family members from both sides should be balanced across tables.",
            "Seat all guests before the timer runs out to complete the level.",
            "If time expires, the wedding is ruined and the bride cries!",
        ]
        y = 250
        for i, line in enumerate(instructions):
            # Bullet icon
            bullet_color = SOFT_GREEN if i < 3 else SOFT_PINK if i < 6 else SOFT_RED
            bullet = font_rule.render("•", True, bullet_color)
            self.screen.blit(bullet, (260, y))
            # Text
            text_surf = font_rule.render(line, True, TEXT_NAME)
            self.screen.blit(text_surf, (285, y))
            y += 34

        # Divider
        pygame.draw.line(self.screen, PANEL_BORDER, (200, y + 10), (SCREEN_W - 200, y + 10), 1)

        # TIPS section
        font_tip_title = pygame.font.SysFont("segoeui", 20, bold=True)
        tip_title = font_tip_title.render("Tips", True, GOLD)
        tip_rect = tip_title.get_rect(center=(SCREEN_W // 2, y + 40))
        self.screen.blit(tip_title, tip_rect)

        font_tip = pygame.font.SysFont("segoeui", 14)
        tips = [
            "Social and Entertainer guests boost table fun when grouped together.",
            "Quiet guests get uncomfortable at loud, crowded tables.",
            "Ex-partners at the same table = instant major crisis!",
            "Watch for the ⚠ icon — it means that guest has conflicts.",
        ]
        tip_y = y + 65
        for tip in tips:
            tip_surf = font_tip.render(f"  ★  {tip}", True, TEXT_TYPE)
            self.screen.blit(tip_surf, (260, tip_y))
            tip_y += 26

        # Start button
        self._btn_intro_start.rect.center = (SCREEN_W // 2, 660)
        self._btn_intro_start.draw(self.screen)

    # ─── Gameplay Screen ──────────────────────────────────────────────────

    def _render_gameplay(self):
        # Build table data for renderer
        level_data = self._get_level_data()
        table_count = level_data.get("table_count", 3)
        tables_data = []
        for tid in range(table_count):
            seated = [None] * 5
            for si in range(5):
                gname = self.table_seats.get((tid, si))
                if gname:
                    seated[si] = gname
            tables_data.append({"seated_guests": seated, "highlight_seats": {}})

        # Draw hall
        self.hall.draw_background()
        self.hall.draw_zones()
        self.table_info = self.hall.draw_tables(self.current_level, tables_data)

        # Draw UI
        if self.panel:
            self.panel.draw(self.screen)
        if self.timer:
            self.timer.draw(self.screen)
        if self.score_display:
            self.score_display.draw(self.screen)

        # Level indicator
        font_lvl = pygame.font.SysFont("segoeui", 13, bold=True)
        lvl_surf = font_lvl.render(f"LEVEL {self.current_level}", True, GOLD)
        self.screen.blit(lvl_surf, (SCREEN_W // 2 - 30, 4))

    # ─── Level Result Screen ─────────────────────────────────────────────

    def _render_result(self):
        self.screen.fill(DARK_BG)

        scores = self.level_scores or {}

        # Title
        font_big = pygame.font.SysFont("segoeui", 36, bold=True)
        title = font_big.render(f"Level {self.current_level} Complete!", True, GOLD)
        title_rect = title.get_rect(center=(SCREEN_W // 2, 60))
        self.screen.blit(title, title_rect)

        # Total score
        total = scores.get("total_score", 0)
        font_total = pygame.font.SysFont("segoeui", 48, bold=True)
        color = SOFT_GREEN if total >= 0 else SOFT_RED
        total_surf = font_total.render(f"{total:.1f}", True, color)
        total_rect = total_surf.get_rect(center=(SCREEN_W // 2, 130))
        self.screen.blit(total_surf, total_rect)

        font_label = pygame.font.SysFont("segoeui", 14)
        lbl = font_label.render("TOTAL SCORE", True, TEXT_DIM)
        lbl_rect = lbl.get_rect(center=(SCREEN_W // 2, 165))
        self.screen.blit(lbl, lbl_rect)

        # Star rating
        stars = 1 if total < 20 else 2 if total < 50 else 3
        font_star = pygame.font.SysFont("segoeui", 36)
        star_text = "★" * stars + "☆" * (3 - stars)
        star_surf = font_star.render(star_text, True, GOLD)
        star_rect = star_surf.get_rect(center=(SCREEN_W // 2, 210))
        self.screen.blit(star_surf, star_rect)

        # Score breakdown
        pygame.draw.line(self.screen, PANEL_BORDER, (340, 245), (940, 245), 1)

        categories = [
            ("Happiness", scores.get("happiness", 0), SOFT_GREEN),
            ("Entertainment", scores.get("entertainment", 0), SOFT_GREEN),
            ("Family Balance", scores.get("family_balance", 0), SOFT_GREEN),
            ("VIP Satisfaction", scores.get("vip_satisfaction", 0), SOFT_GREEN),
            ("Hidden Bonuses", scores.get("hidden_bonuses", 0), SOFT_GREEN),
            ("Tension", -scores.get("tension", 0), SOFT_RED),
            ("Gossip", -scores.get("gossip", 0), SOFT_RED),
            ("Major Crisis", -scores.get("major_crisis", 0), SOFT_RED),
        ]

        font_cat = pygame.font.SysFont("segoeui", 16)
        font_val = pygame.font.SysFont("segoeui", 18, bold=True)
        y = 260
        cx = SCREEN_W // 2

        for cat_name, val, col in categories:
            # Label
            cat_surf = font_cat.render(cat_name, True, TEXT_NAME)
            self.screen.blit(cat_surf, (cx - 180, y))

            # Bar
            bar_x = cx + 40
            bar_w = 200
            bar_h = 16
            pygame.draw.rect(self.screen, (40, 15, 25), (bar_x, y + 2, bar_w, bar_h), border_radius=4)
            fill = min(bar_w, max(0, int(bar_w * abs(val) / 80))) if val != 0 else 0
            if fill > 0:
                pygame.draw.rect(self.screen, col, (bar_x, y + 2, fill, bar_h), border_radius=4)

            # Value
            sign = "+" if val >= 0 else ""
            val_surf = font_val.render(f"{sign}{val}", True, col)
            self.screen.blit(val_surf, (bar_x + bar_w + 10, y - 2))

            y += 32

        # Penalties
        penalties = scores.get("penalties", [])
        if penalties:
            font_pen = pygame.font.SysFont("segoeui", 12)
            pen_y = y + 10
            pen_label = font_cat.render("Violations:", True, SOFT_RED)
            self.screen.blit(pen_label, (cx - 180, pen_y))
            for p in penalties[:3]:
                pen_y += 20
                pen_surf = font_pen.render(f"• {p}", True, (200, 120, 120))
                self.screen.blit(pen_surf, (cx - 160, pen_y))

        # Next button
        btn_text = "NEXT LEVEL" if self.current_level < self.max_levels else "FINISH"
        self._btn_next.text = btn_text
        self._btn_next.rect.center = (SCREEN_W // 2, 620)
        self._btn_next.draw(self.screen)

    # ─── Win Screen ──────────────────────────────────────────────────────

    def _render_win(self):
        if not self.hall.draw_screen_image("good_end"):
            self.screen.fill(DARK_BG)

        # Overlay
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        self.screen.blit(overlay, (0, 0))

        # Title
        font_big = pygame.font.SysFont("segoeui", 48, bold=True)
        title = font_big.render("Wedding Saved!", True, GOLD)
        title_rect = title.get_rect(center=(SCREEN_W // 2, 160))
        self.screen.blit(title, title_rect)

        # Hearts
        font_heart = pygame.font.SysFont("segoeui", 36)
        hearts = font_heart.render("♥  ♥  ♥", True, (255, 120, 150))
        hearts_rect = hearts.get_rect(center=(SCREEN_W // 2, 220))
        self.screen.blit(hearts, hearts_rect)

        # Final score
        total = sum(self.level_total_scores) if self.level_total_scores else 0
        font_score = pygame.font.SysFont("segoeui", 36, bold=True)
        score_surf = font_score.render(f"Final Score: {total:.1f}", True, SOFT_GREEN)
        score_rect = score_surf.get_rect(center=(SCREEN_W // 2, 300))
        self.screen.blit(score_surf, score_rect)

        # Per-level breakdown
        font_lvl = pygame.font.SysFont("segoeui", 18)
        for i, s in enumerate(self.level_total_scores):
            lvl_surf = font_lvl.render(f"Level {i + 1}: {s:.1f}", True, TEXT_NAME)
            lvl_rect = lvl_surf.get_rect(center=(SCREEN_W // 2, 360 + i * 30))
            self.screen.blit(lvl_surf, lvl_rect)

        # Star rating
        avg = total / max(1, len(self.level_total_scores))
        stars = 1 if avg < 20 else 2 if avg < 50 else 3
        font_star = pygame.font.SysFont("segoeui", 48)
        star_text = "★" * stars + "☆" * (3 - stars)
        star_surf = font_star.render(star_text, True, GOLD)
        star_rect = star_surf.get_rect(center=(SCREEN_W // 2, 480))
        self.screen.blit(star_surf, star_rect)

        # Menu button
        self._btn_menu.rect.center = (SCREEN_W // 2, 560)
        self._btn_menu.draw(self.screen)

    # ─── Lose Screen ─────────────────────────────────────────────────────

    def _render_lose(self):
        if self._lose_phase == 0:
            # Fade to black over the gameplay
            self._render_gameplay()
            self.hall.draw_fade_overlay(self._lose_fade_alpha)

        elif self._lose_phase == 1:
            # Show Fail1 as animated GIF
            dt_ms = self._lose_timer * 1000  # not ideal but we reset timer
            frame = self.hall.images.get_gif_frame("Fail1.gif", dt_ms=16)
            if frame:
                self.screen.blit(frame, (0, 0))
            else:
                self.screen.fill(BLACK)

            # "TIME'S UP" text
            overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 80))
            self.screen.blit(overlay, (0, 0))

            font_big = pygame.font.SysFont("segoeui", 52, bold=True)
            text = font_big.render("TIME'S UP!", True, SOFT_RED)
            text_rect = text.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 - 40))
            self.screen.blit(text, text_rect)

            font_sub = pygame.font.SysFont("segoeui", 20)
            sub = font_sub.render("The wedding is ruined...", True, SOFT_PINK)
            sub_rect = sub.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 + 20))
            self.screen.blit(sub, sub_rect)

        elif self._lose_phase >= 2:
            # Show Fail2 as animated GIF (or Fail1 fallback)
            frame = self.hall.images.get_gif_frame("Fail2.gif", dt_ms=16)
            if not frame:
                frame = self.hall.images.get_gif_frame("Fail1.gif", dt_ms=16)
            if frame:
                self.screen.blit(frame, (0, 0))
            else:
                self.screen.fill(BLACK)

            overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 100))
            self.screen.blit(overlay, (0, 0))

            font_big = pygame.font.SysFont("segoeui", 40, bold=True)
            text = font_big.render("The bride is crying...", True, SOFT_PINK)
            text_rect = text.get_rect(center=(SCREEN_W // 2, 80))
            self.screen.blit(text, text_rect)

            # Retry button
            self._btn_retry.rect.center = (SCREEN_W // 2, SCREEN_H - 80)
            self._btn_retry.draw(self.screen)
