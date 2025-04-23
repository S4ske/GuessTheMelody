from abc import ABCMeta, abstractmethod
from datetime import datetime, timedelta
from typing import Tuple

from . import MelodyDTO, PlayerDTO


class StateInfoProviderABC(metaclass=ABCMeta):
	@abstractmethod
	def set_new_state(
		self,
		state: str,
		time_left: timedelta | None = None,
		end_time: datetime | None = None,
		start_time: datetime | None = None,
		category_and_points: Tuple[str, int] | None = None,
		choosing_player_nickname: str | None = None,
		answering_player_nickname: str | None = None,
		answer: str | None = None,
		answered_players_nicknames: list[str] | None = None,
	) -> None:
		pass

	@abstractmethod
	def player_already_answered(self, nickname: str) -> bool:
		pass

	@property
	@abstractmethod
	def state(self) -> str:
		pass

	@state.setter
	@abstractmethod
	def state(self, value: str) -> None:
		pass

	@property
	@abstractmethod
	def time_left(self) -> timedelta:
		pass

	@time_left.setter
	@abstractmethod
	def time_left(self, value: timedelta) -> None:
		pass

	@property
	@abstractmethod
	def end_time(self) -> datetime:
		pass

	@end_time.setter
	@abstractmethod
	def end_time(self, value: datetime) -> None:
		pass

	@property
	@abstractmethod
	def start_time(self) -> datetime:
		pass

	@start_time.setter
	@abstractmethod
	def start_time(self, value: datetime) -> None:
		pass

	@property
	@abstractmethod
	def current_melody(self) -> MelodyDTO:
		pass

	@current_melody.setter
	@abstractmethod
	def current_melody(self, value: MelodyDTO) -> None:
		pass

	@property
	@abstractmethod
	def choosing_player(self) -> PlayerDTO:
		pass

	@choosing_player.setter
	@abstractmethod
	def choosing_player(self, value) -> None:
		pass

	@property
	@abstractmethod
	def answering_player(self) -> PlayerDTO:
		pass

	@answering_player.setter
	@abstractmethod
	def answering_player(self, value) -> None:
		pass

	@property
	@abstractmethod
	def answer(self) -> str:
		pass

	@answer.setter
	@abstractmethod
	def answer(self, value: str) -> None:
		pass

	@property
	@abstractmethod
	def answered_players(self) -> list[PlayerDTO]:
		pass

	@answered_players.setter
	@abstractmethod
	def answered_players(self, value) -> None:
		pass

	@abstractmethod
	def append_answered_player(self, nickname: str) -> None:
		pass

	@abstractmethod
	def set_choosing_player(self, nickname: str) -> None:
		pass
