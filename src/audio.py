from __future__ import annotations

from typing import Optional


class AudioManager:
    def __init__(self) -> None:
        self.background_music_path: Optional[str] = None
        self.place_sound_path: Optional[str] = None
        self.penalty_sound_path: Optional[str] = None
        self.warning_sound_path: Optional[str] = None
        self.win_sound_path: Optional[str] = None
        self.lose_sound_path: Optional[str] = None

        self.is_background_playing = False
        self.is_warning_playing = False
        self.is_muted = False

    def load_sounds(
        self,
        background_music: str = "sounds/background_music.mp3",
        place_sound: str = "sounds/place_guest.wav",
        penalty_sound: str = "sounds/penalty_buzzer.wav",
        warning_sound: str = "sounds/timer_warning.wav",
        win_sound: str = "sounds/win_jingle.wav",
        lose_sound: str = "sounds/lose_sad.wav",
    ) -> None:
        self.background_music_path = background_music
        self.place_sound_path = place_sound
        self.penalty_sound_path = penalty_sound
        self.warning_sound_path = warning_sound
        self.win_sound_path = win_sound
        self.lose_sound_path = lose_sound

    def mute(self) -> None:
        self.is_muted = True
        self.is_background_playing = False
        self.is_warning_playing = False
        print("Audio muted.")

    def unmute(self) -> None:
        self.is_muted = False
        print("Audio unmuted.")

    def play_background_music(self) -> None:
        if self.is_muted:
            return
        self.is_background_playing = True
        print(f"Playing background music: {self.background_music_path}")

    def stop_background_music(self) -> None:
        self.is_background_playing = False
        print("Stopping background music.")

    def play_guest_placement_sound(self) -> None:
        if self.is_muted:
            return
        print(f"Playing placement sound: {self.place_sound_path}")

    def play_penalty_sound(self) -> None:
        if self.is_muted:
            return
        print(f"Playing penalty sound: {self.penalty_sound_path}")

    def play_timer_warning_sound(self) -> None:
        if self.is_muted or self.is_warning_playing:
            return
        self.is_warning_playing = True
        print(f"Playing timer warning sound: {self.warning_sound_path}")

    def stop_timer_warning_sound(self) -> None:
        if self.is_warning_playing:
            self.is_warning_playing = False
            print("Stopping timer warning sound.")

    def play_win_sound(self) -> None:
        if self.is_muted:
            return
        print(f"Playing win sound: {self.win_sound_path}")

    def play_lose_sound(self) -> None:
        if self.is_muted:
            return
        print(f"Playing lose sound: {self.lose_sound_path}")

    def handle_game_event(self, event_name: str) -> None:
        if event_name == "game_start":
            self.play_background_music()
        elif event_name == "guest_placed":
            self.play_guest_placement_sound()
        elif event_name == "penalty":
            self.play_penalty_sound()
        elif event_name == "timer_warning":
            self.play_timer_warning_sound()
        elif event_name == "timer_safe":
            self.stop_timer_warning_sound()
        elif event_name == "win":
            self.play_win_sound()
        elif event_name == "lose":
            self.play_lose_sound()