from player_abc import PlayerABC


class DefaultPlayer(PlayerABC):
    def __init__(self, nickname: str) -> None:
        self._nickname = nickname
        self._point = 0

    def add_points(self, points_count: int) -> None:
        self._point += points_count

    def remove_points(self, points_count: int) -> None:
        self._point -= points_count

    @property
    def points(self) -> int:
        return self._point

    @property
    def nickname(self):
        return self._nickname
