from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from exceptions import PlayerAlreadyAnsweredError, StateError, WrongPlayerChoosingError
from game_state_abc import GameStateABC
from melody_abc import MelodyABC
from player_abc import PlayerABC

if TYPE_CHECKING:
    from . import GuessTheMelodyGame


class MelodyPickState(GameStateABC):
    def __init__(self, game: 'GuessTheMelodyGame', choosing_player: PlayerABC) -> None:
        super().__init__(game)
        self._choosing_player = choosing_player

    @property
    def choosing_player(self) -> PlayerABC:
        return self._choosing_player

    def pick_melody(self, player: PlayerABC, melody: MelodyABC) -> None:
        if player != self._choosing_player:
            raise WrongPlayerChoosingError()
        melody.set_is_guessed()
        next_state = MelodyListeningState(self._game, melody, self._choosing_player,
                                          listening_time=self._game.listening_time)
        self._game.set_state(next_state)


class MelodyListeningState(GameStateABC):
    def __init__(self, game: 'GuessTheMelodyGame',
                 melody: MelodyABC,
                 chosen_player: PlayerABC,
                 already_answered_players: list[PlayerABC] | None = None,
                 listening_time: timedelta = timedelta(milliseconds=30 * 1000)) -> None:
        super().__init__(game)
        self._melody = melody
        self._start_time = datetime.now()
        self._end_time = self._start_time + listening_time
        self._already_answered_players = already_answered_players if already_answered_players else []
        self._choosing_player = chosen_player

    def update_state(self) -> None:
        if datetime.now() > self._end_time:
            self._change_state()

    @property
    def end_time(self):
        if self._time_is_out():
            self._change_state()
            return self._game.end_time
        else:
            return self._end_time

    @property
    def current_melody(self) -> MelodyABC:
        if self._time_is_out():
            self._change_state()
            return self._game.current_melody
        else:
            return self._melody

    def answer(self, player: PlayerABC, answer: str) -> None:
        if self._time_is_out():
            self._change_state()
            self._game.answer(player, answer)
        else:
            if player in self._already_answered_players:
                raise PlayerAlreadyAnsweredError()
            self._already_answered_players.append(player)
            next_state = AnswerCheckState(self._game, self._melody, player, answer, self._end_time - datetime.now(),
                                          self._already_answered_players, self._choosing_player)
            self._game.set_state(next_state)

    @property
    def already_answered_players(self):
        return self._already_answered_players

    def _time_is_out(self):
        return datetime.now() > self._end_time

    def pick_melody(self, player: PlayerABC, melody: MelodyABC) -> None:
        if self._time_is_out():
            self._change_state()
            self._game.pick_melody(player, melody)
        else:
            raise StateError()

    def get_answer(self) -> str:
        if self._time_is_out():
            self._change_state()
            return self._game.get_answer()
        else:
            raise StateError()

    def accept_answer(self) -> None:
        if self._time_is_out():
            self._change_state()
            self._game.accept_answer()
        else:
            raise StateError()

    def reject_answer(self) -> None:
        if self._time_is_out() or len(self._already_answered_players) >= len(self._game.players):
            self._change_state()
            self._game.reject_answer()
        else:
            raise StateError()

    def _change_state(self):
        if self._game.not_guessed_melodies_count <= 0:
            self._game.set_state(IsFinishedState(self._game))
        self._game.set_state(MelodyPickState(self._game, self._choosing_player))


class AnswerCheckState(GameStateABC):
    def __init__(self, game: 'GuessTheMelodyGame', melody: MelodyABC, answered_player: PlayerABC, answer: str,
                 time_left: timedelta, already_answered_players: list[PlayerABC], choosing_player: PlayerABC) -> None:
        super().__init__(game)
        self._answered_player = answered_player
        self._answer = answer
        self._time_left = time_left
        self._melody = melody
        self._already_answered_players = already_answered_players
        self._choosing_player = choosing_player

    def get_answer(self) -> str:
        return self._answer

    def accept_answer(self) -> None:
        next_state = MelodyPickState(self._game, self._answered_player)
        self._answered_player.add_points(self._melody.points)
        self._game.set_state(next_state)

    def reject_answer(self) -> None:
        next_state = MelodyListeningState(self._game, self._melody, self._choosing_player,
                                          self._already_answered_players, self._time_left)
        self._answered_player.remove_points(self._melody.points)
        self._game.set_state(next_state)

    def _change_state(self):
        if self._game.not_guessed_melodies_count <= 0:
            self._game.set_state(IsFinishedState(self._game))
        self._game.set_state(MelodyPickState(self._game, self._choosing_player))


class IsFinishedState(GameStateABC):
    pass
