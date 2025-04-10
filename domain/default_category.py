from typing import Callable

from category_abc import CategoryABC
from melody_abc import MelodyABC


class DefaultCategory(CategoryABC):
    def __init__(self, name: str, melodies: list[MelodyABC]) -> None:
        self._melodies = melodies
        self._name = name

    def _get_melodies_by_condition(self, condition: Callable[[MelodyABC], bool]) -> list[MelodyABC]:
        return list(filter(condition, self._melodies))

    def get_all_melodies(self) -> list[MelodyABC]:
        return self._get_melodies_by_condition(lambda melody: True)

    def get_guessed_melodies(self) -> list[MelodyABC]:
        return self._get_melodies_by_condition(lambda melody: melody.is_guessed)

    def get_not_guessed_melodies(self) -> list[MelodyABC]:
        return self._get_melodies_by_condition(lambda melody: not melody.is_guessed)

    @property
    def not_guessed_melodies_count(self) -> int:
        return len(self.get_not_guessed_melodies())

    @property
    def melodies(self) -> list[MelodyABC]:
        return self._melodies

    @property
    def name(self) -> str:
        return self._name

    def get_available_points(self) -> int:
        return sum(map(lambda melody: melody.points, filter(lambda melody: not melody.is_guessed, self._melodies)))
