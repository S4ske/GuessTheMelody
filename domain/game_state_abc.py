from abc import ABCMeta
from datetime import datetime
from typing import TYPE_CHECKING

from exceptions import StateError
from melody_abc import MelodyABC
from player_abc import PlayerABC

if TYPE_CHECKING:
    from . import GuessTheMelodyGame


class GameStateABC(metaclass=ABCMeta):
    def __init__(self, game: 'GuessTheMelodyGame') -> None:
        self._game = game

    def pick_melody(self, player: PlayerABC, melody: MelodyABC) -> None:
        raise StateError()

    @property
    def choosing_player(self) -> PlayerABC:
        raise StateError()

    @property
    def end_time(self) -> datetime:
        raise StateError()

    def update_state(self) -> None:
        return

    @property
    def already_answered_players(self) -> list[PlayerABC]:
        raise StateError()

    @property
    def current_melody(self) -> MelodyABC:
        raise StateError()

    def answer(self, player: PlayerABC, answer: str) -> None:
        raise StateError()

    def get_answer(self) -> str:
        raise StateError()

    def accept_answer(self) -> None:
        raise StateError()

    def reject_answer(self) -> None:
        raise StateError()
