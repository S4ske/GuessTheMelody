from domain import CategoriesProviderABC, CategoryDTO, MelodyDTO

from ..models import Category, Melody


class CategoriesProvider(CategoriesProviderABC):
	def __init__(self, game_id: int):
		self._game_id = game_id

	@property
	def game_id(self):
		return self._game_id

	def get_category_melodies(self, category_name: str) -> list[MelodyDTO]:
		melodies = Melody.objects.select_related('category').filter(
			category__name=category_name, category__game__pk=self._game_id
		)
		return list(
			map(
				lambda x: MelodyDTO(
					name=x.name,
					points=x.points,
					file=x.link,
					is_guessed=x.is_guessed,
					category=x.category.name,
				),
				melodies,
			)
		)

	def get_category(self, category_name: str) -> CategoryDTO:
		return CategoryDTO(category_name)

	def set_melody_is_guessed(self, category_name: str, points: int) -> None:
		melody = Melody.objects.select_related('category').get(
			category__name=category_name, points=points, category__game__pk=self._game_id
		)
		melody.is_guessed = True
		melody.save()

	def get_melody(self, category_name: str, points: int) -> MelodyDTO:
		melody = Melody.objects.select_related('category').get(
			category__name=category_name, points=points, category__game__pk=self._game_id
		)
		return MelodyDTO(
			name=melody.name,
			points=melody.points,
			file=melody.link,
			is_guessed=melody.is_guessed,
			category=CategoryDTO(name=melody.category.name),
		)

	def get_categories_names(self) -> list[str]:
		return list(
			map(lambda x: x.name, Category.objects.filter(game__pk=self._game_id))
		)

	def get_categories(self) -> list[CategoryDTO]:
		return list(
			map(
				lambda x: CategoryDTO(x.name),
				Category.objects.filter(game__pk=self._game_id),
			)
		)

	def _get_melodies(self, is_guessed: bool) -> list[MelodyDTO]:
		return list(
			map(
				lambda x: MelodyDTO(
					name=x.name,
					points=x.points,
					file=x.link,
					is_guessed=x.is_guessed,
					category=x.category.name,
				),
				Melody.objects.select_related(
					'category'
				).filter(is_guessed=is_guessed, category__game__pk=self._game_id),
			)
		)

	def get_guessed_melodies(self) -> list[MelodyDTO]:
		return self._get_melodies(True)

	def get_not_guessed_melodies(self) -> list[MelodyDTO]:
		return self._get_melodies(False)

	def _get_melodies_count(self, is_guessed: bool) -> int:
		return Melody.objects.filter(is_guessed=is_guessed, category__game__pk=self._game_id).count()

	def get_not_guessed_melodies_count(self) -> int:
		return self._get_melodies_count(False)

	def get_guessed_melodies_count(self) -> int:
		return self._get_melodies_count(True)
