from abc import ABCMeta, abstractmethod

from . import PlayerDTO


class PlayersProviderABC(metaclass=ABCMeta):
	@property
	@abstractmethod
	def players_count(self) -> int:
		pass

	@abstractmethod
	def add_points(self, nickname: str, points_count: int) -> None:
		pass

	@abstractmethod
	def remove_points(self, nickname: str, points_count: int) -> None:
		pass

	@abstractmethod
	def get_random_nickname(self) -> str:
		pass

	@abstractmethod
	def get_points(self, nickname: str) -> int:
		pass

	@abstractmethod
	def get_player(self, nickname: str) -> PlayerDTO:
		pass

	@abstractmethod
	def get_all_players(self) -> list[PlayerDTO]:
		pass
