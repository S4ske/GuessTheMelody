from datetime import datetime, timedelta

from category_abc import CategoryABC
from game_state_abc import GameStateABC
from game_states import MelodyPickState
from melody_abc import MelodyABC
from player_abc import PlayerABC


class GuessTheMelodyGame:
    def __init__(self, players: list[PlayerABC], categories: list[CategoryABC], state: GameStateABC | None = None,
                 listening_time: timedelta = timedelta(milliseconds=30 * 1000)):
        self._players = players
        self._categories = categories
        self._state = state if state else MelodyPickState(self, self._players[0])
        self.listening_time = listening_time

    @property
    def choosing_player(self) -> PlayerABC:
        return self._state.choosing_player

    @property
    def players(self):
        return self._players

    @property
    def categories(self):
        return self._categories

    @property
    def end_time(self) -> datetime:
        return self._state.end_time

    @property
    def already_answered_players(self) -> list[PlayerABC]:
        return self._state.already_answered_players

    def pick_melody(self, player: PlayerABC, melody: MelodyABC) -> None:
        self._state.pick_melody(player, melody)

    @property
    def current_melody(self) -> MelodyABC:
        return self._state.current_melody

    def answer(self, player: PlayerABC, answer: str) -> None:
        self._state.answer(player, answer)

    def get_answer(self) -> str:
        return self._state.get_answer()

    def accept_answer(self):
        self._state.accept_answer()

    def reject_answer(self):
        self._state.reject_answer()

    def set_state(self, state: GameStateABC) -> None:
        self._state = state

    def get_all_melodies(self) -> dict[CategoryABC, list[MelodyABC]]:
        categories_to_melodies = dict()

        for category in self._categories:
            categories_to_melodies[category] = category.get_all_melodies()

        return categories_to_melodies

    def get_guessed_melodies(self) -> dict[CategoryABC, list[MelodyABC]]:
        categories_to_melodies = dict()

        for category in self._categories:
            categories_to_melodies[category] = category.get_guessed_melodies()

        return categories_to_melodies

    def get_not_guessed_melodies(self) -> dict[CategoryABC, list[MelodyABC]]:
        categories_to_melodies = dict()

        for category in self._categories:
            categories_to_melodies[category] = category.get_not_guessed_melodies()

        return categories_to_melodies

    def update_state(self) -> None:
        self._state.update_state()

    @property
    def state(self) -> GameStateABC:
        return self._state

    @property
    def not_guessed_melodies_count(self) -> int:
        return sum(map(lambda category: category.not_guessed_melodies_count, self._categories))
