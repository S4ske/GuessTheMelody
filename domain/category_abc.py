from abc import ABCMeta, abstractmethod

from melody_abc import MelodyABC


class CategoryABC(metaclass=ABCMeta):
    @property
    @abstractmethod
    def melodies(self) -> list[MelodyABC]:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def get_all_melodies(self) -> list[MelodyABC]:
        pass

    @abstractmethod
    def get_guessed_melodies(self) -> list[MelodyABC]:
        pass

    @abstractmethod
    def get_not_guessed_melodies(self) -> list[MelodyABC]:
        pass

    @property
    @abstractmethod
    def not_guessed_melodies_count(self) -> int:
        pass
