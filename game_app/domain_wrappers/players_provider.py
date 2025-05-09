from random import randint

from domain import PlayerDTO, PlayersProviderABC

from ..models import Player


class PlayersProvider(PlayersProviderABC):
    def __init__(self, game_id: int):
        self._game_id = game_id

    def get_all_players(self) -> list[PlayerDTO]:
        return [PlayerDTO(nickname=player.nickname, points=player.points, is_master=player.is_master)
                for player in Player.objects.filter(game__pk=self._game_id, is_master=False).all()]

    @property
    def players_count(self) -> int:
        return Player.objects.filter(game__pk=self._game_id, is_master=False).count()

    def add_points(self, nickname: str, points: int) -> None:
        player = Player.objects.get(game__pk=self._game_id, nickname=nickname, is_master=False)
        player.points += points
        player.save()

    def remove_points(self, nickname: str, points: int) -> None:
        player = Player.objects.get(game__pk=self._game_id, nickname=nickname, is_master=False)
        player.points -= points
        player.save()

    def get_random_nickname(self) -> str:
        players = Player.objects.filter(game__pk=self._game_id, is_master=False)
        return players[randint(0, len(players) - 1)].nickname

    def get_points(self, nickname: str) -> int:
        return Player.objects.get(game__pk=self._game_id, nickname=nickname, is_master=False).points

    def get_player(self, nickname: str) -> PlayerDTO:
        player = Player.objects.get(game__pk=self._game_id, nickname=nickname, is_master=False)
        return PlayerDTO(
            nickname=player.nickname,
            is_master=player.is_master,
            points=player.points,
        )
