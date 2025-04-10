from typing import Any

from melody_abc import MelodyABC


class DefaultMelody(MelodyABC):
    def __init__(self, name: str, file: Any, points: int) -> None:
        self._is_guessed = False
        self._name = name
        self._file = file
        self._points = points

    @property
    def is_guessed(self):
        return self._is_guessed

    @property
    def music_file(self) -> Any:
        return self._file

    def set_is_guessed(self) -> None:
        self._is_guessed = True

    @property
    def points(self) -> int:
        return self._points

    @property
    def name(self) -> str:
        return self._name
