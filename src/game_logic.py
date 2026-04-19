from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set

from src.optimizer import solve
import src.scoring as scoring_module


def _guest_identifier(guest: Dict[str, Any]) -> str:
    """
    Guest için kullanılacak tekil anahtar.
    Önce id, yoksa name, o da yoksa guest_x üretir.
    """
    if "id" in guest and guest["id"] is not None:
        return str(guest["id"])
    if "name" in guest and guest["name"] is not None:
        return str(guest["name"])
    return f"guest_{id(guest)}"


def _normalize_guest_list(guests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Elimizdeki guest datasını scoring/optimizer ile uyumlu hale getirir.
    Eğer id yoksa name'i id olarak kopyalar.
    """
    normalized = []

    for guest in guests:
        g = dict(guest)

        gid = _guest_identifier(g)
        g["id"] = gid

        if "name" not in g or g["name"] is None:
            g["name"] = gid

        for key in ["likes", "dislikes", "must_sit_with", "cannot_sit_with", "groups"]:
            if key not in g or g[key] is None:
                g[key] = []

        if "type" not in g or g["type"] is None:
            g["type"] = "guest"

        normalized.append(g)

    return normalized


def _normalize_level_data(level_data: Dict[str, Any], guests: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Level datasında eksik alanları tamamlar.
    scoring.py'nin beklediği yapıya uydurur.
    """
    level_copy = dict(level_data)

    guest_ids = [_guest_identifier(g) for g in guests]

    if "guest_ids" not in level_copy:
        level_copy["guest_ids"] = guest_ids

    if "tables" not in level_copy:
        table_count = level_copy.get("table_count", 3)
        table_capacity = level_copy.get("table_capacity", 5)

        level_copy["tables"] = [
            {"table_id": f"Table {i + 1}", "capacity": table_capacity}
            for i in range(table_count)
        ]

    if "table_count" not in level_copy:
        level_copy["table_count"] = len(level_copy["tables"])

    if "weights" not in level_copy:
        level_copy["weights"] = {
            "happiness": 1.0,
            "entertainment": 1.0,
            "family_balance": 1.0,
            "vip_satisfaction": 1.0,
            "hidden_bonuses": 1.0,
            "tension": -1.0,
            "gossip": -1.0,
            "major_crisis": -5.0,
        }

    if "vip_tables" not in level_copy:
        level_copy["vip_tables"] = []

    return level_copy


def _normalize_score_result(raw_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    scoring.py farklı formatlarda sonuç döndürebilir.
    Tek tip hale getiriyoruz.
    """
    if not isinstance(raw_result, dict):
        return {
            "total_score": 0,
            "penalties": ["Invalid scoring result"],
            "has_major_violation": False,
            "hard_violations": [],
            "components": {},
        }

    hard_violations = raw_result.get("hard_violations", [])
    penalty_trigger = raw_result.get("penalty_trigger", False)
    has_major_violation = raw_result.get("has_major_violation", penalty_trigger or len(hard_violations) > 0)

    penalties = raw_result.get("penalties", [])
    if not penalties and hard_violations:
        penalties = hard_violations

    components = raw_result.get("components", {})
    if not components:
        components = {
            k: v for k, v in raw_result.items()
            if k in {
                "happiness",
                "entertainment",
                "family_balance",
                "vip_satisfaction",
                "hidden_bonuses",
                "tension",
                "gossip",
                "major_crisis",
            }
        }

    return {
        "total_score": raw_result.get("total_score", 0),
        "penalties": penalties,
        "has_major_violation": has_major_violation,
        "hard_violations": hard_violations,
        "components": components,
        "layout": raw_result.get("layout"),
    }


def _call_scoring(layout: Dict[str, List[str]], level_data: Dict[str, Any], guests: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    scoring.py içinde evaluate varsa onu,
    evaluate_layout varsa onu çağırır.
    """
    if hasattr(scoring_module, "evaluate"):
        raw = scoring_module.evaluate(layout, level_data, guests)
        return _normalize_score_result(raw)

    if hasattr(scoring_module, "evaluate_layout"):
        raw = scoring_module.evaluate_layout(layout, guests, level_data)
        return _normalize_score_result(raw)

    raise AttributeError("scoring.py içinde evaluate veya evaluate_layout bulunamadı.")


@dataclass
class PlacementResult:
    valid: bool
    penalty_applied: bool
    penalty_seconds: int
    score_data: Dict[str, Any]
    message: str = ""


@dataclass
class GameState:
    current_level_index: int = 0
    level_data: Optional[Dict[str, Any]] = None
    level_key: Optional[str] = None

    total_levels: int = 0
    score_data: Dict[str, Any] = field(default_factory=dict)

    timer_total: float = 60.0
    timer_remaining: float = 60.0
    started_at: Optional[float] = None
    is_running: bool = False
    is_finished: bool = False
    is_won: bool = False
    last_penalty_time: float = 0.0

    placed_guests: Set[str] = field(default_factory=set)
    remaining_guests: Set[str] = field(default_factory=set)
    layout: Dict[str, List[str]] = field(default_factory=dict)

    hint_table_ids: List[str] = field(default_factory=list)
    optimal_layout: Dict[str, List[str]] = field(default_factory=dict)


class GameStateManager:
    def __init__(self, levels_data: Dict[str, Any], guests_data: Dict[str, Any]):
        self.levels_data = levels_data
        self.guests_data = guests_data

        if "levels" in levels_data:
            self.level_mode = "list"
            self.level_items = levels_data["levels"]
        else:
            self.level_mode = "dict"
            self.level_keys = [k for k in levels_data.keys() if k.startswith("level_")]
            self.level_keys.sort()

        self.state = GameState(total_levels=self._get_total_level_count())

    def _get_total_level_count(self) -> int:
        if getattr(self, "level_mode", None) == "list":
            return len(self.level_items)
        return len(self.level_keys)

    def start_game(self) -> None:
        self.load_level(0)

    def load_level(self, index: int) -> None:
        if index < 0 or index >= self._get_total_level_count():
            raise IndexError("Geçersiz level index.")

        if self.level_mode == "list":
            raw_level_data = self.level_items[index]
            level_key = raw_level_data.get("level_id", f"level_{index + 1}")
        else:
            level_key = self.level_keys[index]
            raw_level_data = self.levels_data[level_key]

        if "guests" in self.guests_data:
            raw_guests = self.guests_data["guests"]
        else:
            raw_guests = self.guests_data[level_key]

        guests = _normalize_guest_list(raw_guests)
        level_data = _normalize_level_data(raw_level_data, guests)

        table_count = level_data.get("table_count", len(level_data.get("tables", [])) or 3)
        layout = {f"Table {i + 1}": [] for i in range(table_count)}

        guest_ids = {_guest_identifier(guest) for guest in guests}

        self.state = GameState(
            current_level_index=index,
            level_data=level_data,
            level_key=level_key,
            total_levels=self._get_total_level_count(),
            timer_total=float(level_data.get("time_limit", 60)),
            timer_remaining=float(level_data.get("time_limit", 60)),
            started_at=time.time(),
            is_running=True,
            is_finished=False,
            is_won=False,
            placed_guests=set(),
            remaining_guests=guest_ids,
            layout=layout,
            hint_table_ids=[],
            score_data={},
        )

        try:
            self.state.optimal_layout = solve(level_data, guests)
        except Exception:
            self.state.optimal_layout = {}

        self._refresh_score()

    def get_current_guests(self) -> List[Dict[str, Any]]:
        if self.level_mode == "list":
            if "guests" in self.guests_data:
                return _normalize_guest_list(self.guests_data["guests"])
            return []

        if not self.state.level_key:
            return []

        return _normalize_guest_list(self.guests_data[self.state.level_key])

    def update_timer(self) -> None:
        if not self.state.is_running or self.state.is_finished:
            return

        elapsed = time.time() - (self.state.started_at or time.time())
        self.state.timer_remaining = max(0.0, self.state.timer_total - elapsed)

        if self.state.timer_remaining <= 0:
            self.state.is_running = False
            self.state.is_finished = True
            self.state.is_won = False

    def place_guest(self, guest_id: str, table_name: str) -> PlacementResult:
        if self.state.is_finished:
            return PlacementResult(False, False, 0, self.state.score_data, "Oyun zaten bitti.")

        if table_name not in self.state.layout:
            return PlacementResult(False, False, 0, self.state.score_data, "Geçersiz masa.")

        if guest_id in self.state.placed_guests:
            return PlacementResult(False, False, 0, self.state.score_data, "Bu misafir zaten yerleştirildi.")

        self.state.layout[table_name].append(guest_id)
        self.state.placed_guests.add(guest_id)
        self.state.remaining_guests.discard(guest_id)

        penalty_applied = False
        penalty_seconds = 0

        result = self._refresh_score()

        if result.get("has_major_violation", False):
            self._apply_penalty(3)
            penalty_applied = True
            penalty_seconds = 3

        if not self.state.remaining_guests and not result.get("has_major_violation", False):
            self.state.is_finished = True
            self.state.is_running = False
            self.state.is_won = True

        return PlacementResult(
            valid=not result.get("has_major_violation", False),
            penalty_applied=penalty_applied,
            penalty_seconds=penalty_seconds,
            score_data=self.state.score_data,
            message="Placement processed."
        )

    def remove_guest(self, guest_id: str) -> bool:
        for table_name, guest_list in self.state.layout.items():
            if guest_id in guest_list:
                guest_list.remove(guest_id)
                self.state.placed_guests.discard(guest_id)
                self.state.remaining_guests.add(guest_id)
                self._refresh_score()
                return True
        return False

    def next_level(self) -> bool:
        next_index = self.state.current_level_index + 1
        if next_index >= self._get_total_level_count():
            return False
        self.load_level(next_index)
        return True

    def restart_current_level(self) -> None:
        self.load_level(self.state.current_level_index)

    def get_hint_for_guest(self, guest_id: str) -> List[str]:
        hinted_tables: List[str] = []

        if self.state.optimal_layout:
            for table_name, guests in self.state.optimal_layout.items():
                if guest_id in guests:
                    hinted_tables.append(table_name)

        self.state.hint_table_ids = hinted_tables
        return hinted_tables

    def get_score(self) -> Dict[str, Any]:
        return self.state.score_data

    def get_display_state(self) -> Dict[str, Any]:
        return {
            "current_level": self.state.level_key,
            "timer_remaining": round(self.state.timer_remaining, 2),
            "placed_guests_count": len(self.state.placed_guests),
            "remaining_guests_count": len(self.state.remaining_guests),
            "placed_guests": list(self.state.placed_guests),
            "remaining_guests": list(self.state.remaining_guests),
            "score_data": self.state.score_data,
            "layout": self.state.layout,
            "hint_tables": self.state.hint_table_ids,
            "is_finished": self.state.is_finished,
            "is_won": self.state.is_won,
        }

    def should_play_warning_sound(self) -> bool:
        return self.state.is_running and not self.state.is_finished and self.state.timer_remaining < 10

    def _apply_penalty(self, seconds: int) -> None:
        self.state.timer_remaining = max(0.0, self.state.timer_remaining - seconds)
        self.state.last_penalty_time = time.time()

        if self.state.timer_remaining <= 0:
            self.state.is_finished = True
            self.state.is_running = False
            self.state.is_won = False

    def _refresh_score(self) -> Dict[str, Any]:
        guests = self.get_current_guests()
        level_data = self.state.level_data or {}

        try:
            self.state.score_data = _call_scoring(self.state.layout, level_data, guests)
        except Exception as exc:
            self.state.score_data = {
                "total_score": 0,
                "penalties": [f"Scoring error: {exc}"],
                "has_major_violation": False,
                "hard_violations": [],
                "components": {},
            }

        return self.state.score_data