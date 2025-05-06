from datetime import datetime, timedelta
from typing import Tuple

from domain import CategoryDTO, MelodyDTO, PlayerDTO, StateInfoProviderABC

from ..models import GameState, GuessTheMelodyGame, Melody, Player


class StateInfoProvider(StateInfoProviderABC):
	def __init__(self, game_id: int):
		self._game_id = game_id

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
		current_melody_id = None
		if category_and_points is not None:
			melody = Melody.objects.get(
				category__game__pk=self._game_id,
				category__name=category_and_points[0],
				points=category_and_points[1],
			)
			current_melody_id = melody.pk
		choosing_player_id = None
		if choosing_player_nickname is not None:
			choosing_player = Player.objects.get(game__pk=self._game_id, nickname=choosing_player_nickname)
			choosing_player_id = choosing_player.pk
		answering_player_id = None
		if answering_player_nickname is not None:
			answering_player = Player.objects.get(game__pk=self._game_id, nickname=answering_player_nickname)
			answering_player_id = answering_player.pk
		game = GuessTheMelodyGame.objects.get(pk=self._game_id)
		old_game_state = GameState.objects.get(game__pk=self._game_id)
		game_state = GameState(
			game=game,
			state=state,
			time_left=time_left.microseconds // 1000 if time_left else None,
			end_time=end_time,
			start_time=start_time,
			current_melody_id=current_melody_id,
			choosing_player_id=choosing_player_id,
			answering_player_id=answering_player_id,
			answer=answer,
			answered_players_ids=list(map(lambda x: x.pk,
										  game.players.filter(nickname__in=answered_players_nicknames)))
			if answered_players_nicknames else []
		)
		old_game_state.delete()
		game_state.save()

	def player_already_answered(self, nickname: str) -> bool:
		game = GuessTheMelodyGame.objects.get(pk=self._game_id)
		player = game.players.get(nickname=nickname)
		return player.pk in game.state.answered_players_ids

	def _get_game_state(self):
		return GameState.objects.get(game__pk=self._game_id)

	@property
	def state(self) -> str:
		game_state = self._get_game_state()
		return game_state.state

	@property
	def time_left(self) -> timedelta:
		game_state = self._get_game_state()
		return timedelta(milliseconds=game_state.time_left)

	@property
	def end_time(self) -> datetime:
		game_state = self._get_game_state()
		return game_state.end_time

	@property
	def start_time(self) -> datetime:
		game_state = self._get_game_state()
		return game_state.start_time

	@property
	def current_melody(self) -> MelodyDTO:
		game_state = self._get_game_state()
		melody = Melody.objects.get(pk=game_state.current_melody_id)
		return MelodyDTO(name=melody.name, points=melody.points, is_guessed=melody.is_guessed,
						 category=CategoryDTO(name=melody.category.name), file=melody.link)

	@property
	def choosing_player(self) -> PlayerDTO:
		game_state = self._get_game_state()
		player = Player.objects.get(pk=game_state.choosing_player_id)
		return PlayerDTO(is_master=player.is_master, nickname=player.nickname, points=player.points)

	@property
	def answering_player(self) -> PlayerDTO:
		game_state = self._get_game_state()
		player = Player.objects.get(pk=game_state.answering_player_id)
		return PlayerDTO(is_master=player.is_master, nickname=player.nickname, points=player.points)

	@property
	def answer(self) -> str:
		game_state = self._get_game_state()
		return game_state.answer

	@property
	def answered_players(self) -> list[PlayerDTO]:
		game_state = self._get_game_state()
		players = Player.objects.filter(pk__in=game_state.answered_players_ids)
		return [PlayerDTO(nickname=player.nickname, is_master=player.is_master, points=player.points)
				for player in players]

	def append_answered_player(self, nickname: str) -> None:
		player = Player.objects.get(nickname=nickname, game__pk=self._game_id)
		game_state = GameState.objects.get(game__pk=self._game_id)
		game_state.answered_players_ids.append(player.pk)
		game_state.save(update_fields=['answered_players_ids'])

	def set_choosing_player(self, nickname: str) -> None:
		player = Player.objects.get(nickname=nickname)
		game_state = GameState.objects.get(game__pk=self._game_id)
		game_state.choosing_player_id = player.pk
		game_state.save()
