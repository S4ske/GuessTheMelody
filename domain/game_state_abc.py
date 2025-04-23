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
	@abstractmethod
	def choosing_player(self) -> PlayerDTO:
		raise StateError()

	@property
	@abstractmethod
	def start_time(self) -> datetime:
		pass

	@property
	@abstractmethod
	def end_time(self) -> datetime:
		raise StateError()

	@abstractmethod
	def update_state(self) -> None:
		return

	@property
	@abstractmethod
	def already_answered_players(self) -> list[PlayerDTO]:
		raise StateError()

	@property
	@abstractmethod
	def current_melody(self) -> MelodyDTO:
		raise StateError()

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
