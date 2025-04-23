from abc import ABCMeta, abstractmethod

from .dto import Category as CategoryDTO, Melody as MelodyDTO


class CategoriesProviderABC(metaclass=ABCMeta):
	@abstractmethod
	def get_category_melodies(self, category_name: str) -> list[MelodyDTO]:
		pass

	@abstractmethod
	def get_category(self, category_name: str) -> CategoryDTO:
		pass

	@abstractmethod
	def set_melody_is_guessed(self, category_name: str, points: int) -> None:
		pass

	@abstractmethod
	def get_melody(self, category_name: str, points: int) -> MelodyDTO:
		pass

	@abstractmethod
	def get_categories_names(self) -> list[str]:
		pass

	@abstractmethod
	def get_categories(self) -> list[CategoryDTO]:
		pass

	@abstractmethod
	def get_guessed_melodies(self) -> list[MelodyDTO]:
		pass

	@abstractmethod
	def get_not_guessed_melodies(self) -> list[MelodyDTO]:
		pass

	@abstractmethod
	def get_not_guessed_melodies_count(self) -> int:
		pass
