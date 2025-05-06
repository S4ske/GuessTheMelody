from datetime import datetime, timezone
from typing import TYPE_CHECKING

from .dto import Melody as MelodyDTO, Player as PlayerDTO
from .exceptions import AlreadyPickedError, PlayerAlreadyAnsweredError, StateError, WrongPlayerChoosingError
from .game_state_abc import GameStateABC
from .game_states_enum import GameStates

if TYPE_CHECKING:
	from . import GuessTheMelodyGame


class MelodyPickState(GameStateABC):
	@property
	def start_time(self) -> datetime:
		raise StateError()

	@property
	def end_time(self) -> datetime:
		raise StateError()

	def update_state(self) -> None:
		return

	@property
	def already_answered_players(self) -> list[PlayerDTO]:
		raise StateError()

	@property
	def current_melody(self) -> MelodyDTO:
		raise StateError()

	def answer(self, player_nickname: str, answer: str) -> None:
		raise StateError()

	def get_answer(self) -> str:
		raise StateError()

	def accept_answer_partially(self) -> None:
		raise StateError()

	def accept_answer(self) -> None:
		raise StateError()

	def reject_answer(self) -> None:
		raise StateError()

	def __init__(self, game: 'GuessTheMelodyGame') -> None:
		super().__init__(game)
		self._players_provider = game._players_provider
		self._categories_provider = game._categories_provider
		self._state_info_provider = game._state_info_provider

	@property
	def choosing_player(self) -> PlayerDTO:
		return self._state_info_provider.choosing_player

	def pick_melody(self, nickname: str, category_name: str, points: int) -> None:
		if nickname != self._state_info_provider.choosing_player.nickname:
			raise WrongPlayerChoosingError()
		melody = self._categories_provider.get_melody(category_name, points)
		if melody.is_guessed:
			raise AlreadyPickedError()

		self._categories_provider.set_melody_is_guessed(category_name, points)
		start_time = datetime.now(timezone.utc)

		self._state_info_provider.set_new_state(
			GameStates.LISTENING.value,
			category_and_points=(melody.category.name, melody.points),
			choosing_player_nickname=self._state_info_provider.choosing_player.nickname,
			start_time=start_time,
			end_time=start_time + self._game.listening_time,
			answered_players_nicknames=[],
		),
		self._game.set_state(MelodyListeningState(self._game))


class MelodyListeningState(GameStateABC):
	@property
	def start_time(self) -> datetime:
		if self._time_is_out():
			self._change_state_if_time_out()
			return self._game.start_time
		return self._state_info_provider.start_time

	@property
	def choosing_player(self) -> PlayerDTO:
		if self._time_is_out():
			self._change_state_if_time_out()
			return self._game.choosing_player
		return self._state_info_provider.choosing_player

	def __init__(
		self,
		game: 'GuessTheMelodyGame'
	) -> None:
		super().__init__(game)
		self._players_provider = game._players_provider
		self._categories_provider = game._categories_provider
		self._state_info_provider = game._state_info_provider

	def update_state(self) -> None:
		if self._time_is_out():
			self._change_state_if_time_out()

	@property
	def end_time(self):
		if self._time_is_out():
			self._change_state_if_time_out()
			return self._game.end_time
		else:
			return self._state_info_provider.end_time

	@property
	def current_melody(self) -> MelodyDTO:
		if self._time_is_out():
			self._change_state_if_time_out()
			return self._game.current_melody
		else:
			return self._state_info_provider.current_melody

	def answer(self, nickname: str, answer: str) -> None:
		if self._time_is_out():
			self._change_state_if_time_out()
			self._game.answer(nickname, answer)
		else:
			if self._state_info_provider.player_already_answered(nickname):
				raise PlayerAlreadyAnsweredError()
			self._state_info_provider.append_answered_player(nickname)
			melody = self._state_info_provider.current_melody

			self._state_info_provider.set_new_state(
				GameStates.ANSWERING.value,
				answering_player_nickname=nickname,
				answer=answer,
				time_left=self._state_info_provider.end_time - datetime.now(timezone.utc),
				category_and_points=(melody.category.name, melody.points),
				answered_players_nicknames=list(map(lambda player: player.nickname, self._state_info_provider.answered_players)),
				choosing_player_nickname=self._state_info_provider.choosing_player.nickname,
			)
			self._game.set_state(AnswerCheckState(self._game))

	@property
	def already_answered_players(self) -> list[PlayerDTO]:
		if self._time_is_out():
			self._change_state_if_time_out()
			return self._game.already_answered_players
		return self._state_info_provider.answered_players

	def _time_is_out(self):
		return datetime.now(timezone.utc) > self._state_info_provider.end_time

	def pick_melody(self, nickname: str, category: str, points: int) -> None:
		if self._time_is_out():
			self._change_state_if_time_out()
			self._game.pick_melody(nickname, category, points)
		else:
			raise StateError()

	def get_answer(self) -> str:
		if self._time_is_out():
			self._change_state_if_time_out()
			return self._game.get_answer()
		else:
			raise StateError()

	def accept_answer_partially(self) -> None:
		if self._time_is_out():
			self._change_state_if_time_out()
			self._game.accept_answer_partially()
		else:
			raise StateError()

	def accept_answer(self) -> None:
		if self._time_is_out():
			self._change_state_if_time_out()
			self._game.accept_answer()
		else:
			raise StateError()

	def reject_answer(self) -> None:
		if (
			self._time_is_out()
			or len(self._state_info_provider.answered_players) >= self._players_provider.players_count
		):
			self._change_state_if_time_out()
			self._game.reject_answer()
		else:
			raise StateError()

	def _change_state_if_time_out(self):
		if self._game.not_guessed_melodies_count <= 0:
			self._state_info_provider.set_new_state(GameStates.FINISHED.value)
			self._game.set_state(IsFinishedState(self._game))
		self._state_info_provider.set_new_state(
			GameStates.CHOOSING.value,
			choosing_player_nickname=self._state_info_provider.choosing_player.nickname,
		)
		self._game.set_state(MelodyPickState(self._game))


class AnswerCheckState(GameStateABC):
	@property
	def start_time(self) -> datetime:
		raise StateError()

	def pick_melody(self, nickname: str, category: str, points: int) -> None:
		raise StateError()

	@property
	def choosing_player(self) -> PlayerDTO:
		raise StateError()

	@property
	def end_time(self) -> datetime:
		raise StateError()

	def update_state(self) -> None:
		return

	@property
	def already_answered_players(self) -> list[PlayerDTO]:
		return self._state_info_provider.answered_players

	@property
	def current_melody(self) -> MelodyDTO:
		return self._state_info_provider.current_melody

	def answer(self, player_nickname: str, answer: str) -> None:
		raise StateError()

	def __init__(
		self,
		game: 'GuessTheMelodyGame',
	) -> None:
		super().__init__(game)
		self._players_provider = game._players_provider
		self._categories_provider = game._categories_provider
		self._state_info_provider = game._state_info_provider

	def get_answer(self) -> str:
		return self._state_info_provider.answer

	def accept_answer_partially(self) -> None:
		self._players_provider.add_points(
			self._state_info_provider.answering_player.nickname, self._state_info_provider.current_melody.points // 2
		)
		melody = self._state_info_provider.current_melody
		start_time = datetime.now(timezone.utc)

		self._state_info_provider.set_new_state(
			GameStates.LISTENING.value,
			category_and_points=(melody.category.name, melody.points),
			choosing_player_nickname=self._state_info_provider.choosing_player.nickname,
			start_time=start_time,
			end_time=start_time + self._state_info_provider.time_left,
			answered_players_nicknames=list(map(lambda x: x.nickname, self._state_info_provider.answered_players)),
		),
		self._game.set_state(MelodyListeningState(self._game))

	def accept_answer(self) -> None:
		player = self._state_info_provider.answering_player
		self._players_provider.add_points(player.nickname, self._state_info_provider.current_melody.points)
		self._state_info_provider.set_new_state(
			GameStates.CHOOSING.value,
			choosing_player_nickname=player.nickname,
		)
		self._game.set_state(MelodyPickState(self._game))

	def reject_answer(self) -> None:
		melody = self._state_info_provider.current_melody
		start_time = datetime.now(timezone.utc)
		self._players_provider.remove_points(self._state_info_provider.answering_player.nickname, melody.points)
		self._state_info_provider.set_new_state(
			GameStates.LISTENING.value,
			category_and_points=(melody.category.name, melody.points),
			choosing_player_nickname=self._state_info_provider.choosing_player.nickname,
			start_time=start_time,
			end_time=start_time + self._state_info_provider.time_left,
			answered_players_nicknames=list(map(lambda x: x.nickname, self._state_info_provider.answered_players)),
		),
		self._game.set_state(MelodyListeningState(self._game))

	def _change_state_(self):
		if self._game.not_guessed_melodies_count <= 0:
			self._state_info_provider.set_new_state(GameStates.FINISHED.value)
			self._game.set_state(IsFinishedState(self._game))
		self._state_info_provider.set_new_state(
			GameStates.CHOOSING.value,
			choosing_player_nickname=self._state_info_provider.choosing_player.nickname,
		)
		self._game.set_state(MelodyPickState(self._game))


class IsFinishedState(GameStateABC):
	@property
	def start_time(self) -> datetime:
		raise StateError()

	def __init__(self, game: 'GuessTheMelodyGame'):
		super().__init__(game)
		self._players_provider = game._players_provider
		self._categories_provider = game._categories_provider
		self._state_info_provider = game._state_info_provider

	def pick_melody(self, nickname: str, category: str, points: int) -> None:
		raise StateError()

	@property
	def choosing_player(self) -> PlayerDTO:
		raise StateError()

	@property
	def end_time(self) -> datetime:
		raise StateError()

	def update_state(self) -> None:
		return

	@property
	def already_answered_players(self) -> list[PlayerDTO]:
		raise StateError()

	@property
	def current_melody(self) -> MelodyDTO:
		raise StateError()

	def answer(self, player_nickname: str, answer: str) -> None:
		raise StateError()

	def get_answer(self) -> str:
		raise StateError()

	def accept_answer_partially(self) -> None:
		raise StateError()

	def accept_answer(self) -> None:
		raise StateError()

	def reject_answer(self) -> None:
		raise StateError()
