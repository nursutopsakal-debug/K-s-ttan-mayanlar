from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class AnimationState:
    guest_hovered: Optional[str] = None
    highlighted_table: Optional[str] = None
    crying_bride_active: bool = False
    score_reveal_active: bool = False
    last_animation: Optional[str] = None


class AnimationController:
    def __init__(self) -> None:
        self.state = AnimationState()

    def trigger_guest_hover(self, guest_id: str) -> Dict[str, str]:
        self.state.guest_hovered = guest_id
        self.state.last_animation = "guest_hover"
        return {
            "animation": "guest_hover",
            "target": guest_id,
            "effect": "scale_up_soft_glow"
        }

    def clear_guest_hover(self) -> None:
        self.state.guest_hovered = None

    def trigger_table_highlight(self, table_name: str) -> Dict[str, str]:
        self.state.highlighted_table = table_name
        self.state.last_animation = "table_highlight"
        return {
            "animation": "table_highlight",
            "target": table_name,
            "effect": "pulse_outline"
        }

    def clear_table_highlight(self) -> None:
        self.state.highlighted_table = None

    def trigger_crying_bride(self) -> Dict[str, str]:
        self.state.crying_bride_active = True
        self.state.last_animation = "crying_bride"
        return {
            "animation": "crying_bride",
            "target": "bride_avatar",
            "effect": "shake_and_tear"
        }

    def stop_crying_bride(self) -> None:
        self.state.crying_bride_active = False

    def trigger_score_reveal(self) -> Dict[str, str]:
        self.state.score_reveal_active = True
        self.state.last_animation = "score_reveal"
        return {
            "animation": "score_reveal",
            "target": "score_panel",
            "effect": "fade_in_count_up"
        }

    def stop_score_reveal(self) -> None:
        self.state.score_reveal_active = False

    def reset_all(self) -> None:
        self.state = AnimationState()

    def get_animation_state(self) -> Dict[str, object]:
        return {
            "guest_hovered": self.state.guest_hovered,
            "highlighted_table": self.state.highlighted_table,
            "crying_bride_active": self.state.crying_bride_active,
            "score_reveal_active": self.state.score_reveal_active,
            "last_animation": self.state.last_animation,
        }