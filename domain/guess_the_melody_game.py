from datetime import datetime, timedelta

from .categories_provider_abc import CategoriesProviderABC
from .dto import Melody as MelodyDTO, Player as PlayerDTO
from .game_state_abc import GameStateABC
from .players_provider_abc import PlayersProviderABC
from .state_info_provider_abc import StateInfoProviderABC


class GuessTheMelodyGame:
	def __init__(
		self,
		players_provider: PlayersProviderABC,
		categories_provider: CategoriesProviderABC,
		state_info_provider: StateInfoProviderABC,
		state: GameStateABC | None = None,
		listening_time: timedelta = timedelta(milliseconds=30 * 1000),
	):
		self._players_provider = players_provider
		self._categories_provider = categories_provider
		self._state_info_provider = state_info_provider
		self._state = state
		self._listening_time = listening_time

	@property
	def listening_time(self):
		return self._listening_time

	@property
	def choosing_player(self) -> PlayerDTO:
		return self._state.choosing_player

	@property
	def players(self) -> list[PlayerDTO]:
		return self._players_provider.get_all_players()

	@property
	def end_time(self) -> datetime:
		return self._state.end_time

	@property
	def start_time(self) -> datetime:
		return self._state.start_time

	@property
	def already_answered_players(self) -> list[PlayerDTO]:
		return self._state.already_answered_players

	def pick_melody(self, nickname: str, category: str, points: int) -> None:
		self._state.pick_melody(nickname, category, points)

	@property
	def current_melody(self) -> MelodyDTO:
		return self._state.current_melody

	def answer(self, nickname: str, answer: str) -> None:
		self._state.answer(nickname, answer)

	def get_answer(self) -> str:
		return self._state.get_answer()

	def accept_answer_partially(self) -> None:
		self._state.accept_answer_partially()

	def accept_answer(self) -> None:
		self._state.accept_answer()

	def reject_answer(self) -> None:
		self._state.reject_answer()

	def set_state(self, state: GameStateABC) -> None:
		self._state = state

	def get_guessed_melodies(self):
		return self._categories_provider.get_guessed_melodies()

	def get_not_guessed_melodies(self):
		return self._categories_provider.get_not_guessed_melodies()

	def update_state(self) -> None:
		self._state.update_state()

	@property
	def state(self) -> GameStateABC:
		return self._state

	@property
	def not_guessed_melodies_count(self) -> int:
		return self._categories_provider.get_not_guessed_melodies_count()
