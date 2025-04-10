from abc import ABCMeta, abstractmethod
from typing import Any


class MelodyABC(metaclass=ABCMeta):
    @property
    @abstractmethod
    def music_file(self) -> Any:
        pass

    @abstractmethod
    def set_is_guessed(self) -> None:
        pass

    @property
    @abstractmethod
    def is_guessed(self):
        pass

    @property
    @abstractmethod
    def points(self) -> int:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass
