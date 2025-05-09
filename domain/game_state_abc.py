from abc import ABCMeta, abstractmethod
from datetime import datetime
from typing import TYPE_CHECKING

from .dto import Melody as MelodyDTO, Player as PlayerDTO
from .exceptions import StateError

if TYPE_CHECKING:
	from . import GuessTheMelodyGame


class GameStateABC(metaclass=ABCMeta):
	def __init__(self, game: 'GuessTheMelodyGame') -> None:
		self._game = game

	@abstractmethod
	def pick_melody(self, nickname: str, category: str, points: int) -> None:
		raise StateError()

	@property
	def answering_player(self) -> PlayerDTO | None:
		return

	@property
	def choosing_player(self) -> PlayerDTO | None:
		return

	@property
	def start_time(self) -> datetime | None:
		return

	@property
	def end_time(self) -> datetime | None:
		return

	@abstractmethod
	def update_state(self) -> None:
		return

	@property
	def already_answered_players(self) -> list[PlayerDTO] | None:
		return

	@property
	def current_melody(self) -> MelodyDTO | None:
		return

	@abstractmethod
	def answer(self, player_nickname: str, answer: str) -> None:
		raise StateError()

	@abstractmethod
	def get_answer(self) -> str:
		raise StateError()

	@abstractmethod
	def accept_answer_partially(self) -> None:
		raise StateError()

	@abstractmethod
	def accept_answer(self) -> None:
		raise StateError()

	@abstractmethod
	def reject_answer(self) -> None:
		raise StateError()
