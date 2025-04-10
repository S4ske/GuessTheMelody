from abc import ABCMeta, abstractmethod


class PlayerABC(metaclass=ABCMeta):
    @abstractmethod
    def add_points(self, points_count: int) -> None:
        pass

    @abstractmethod
    def remove_points(self, points_count: int) -> None:
        pass

    @property
    @abstractmethod
    def points(self) -> int:
        pass
