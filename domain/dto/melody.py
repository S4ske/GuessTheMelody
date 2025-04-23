from dataclasses import dataclass
from typing import Any

from . import Category


@dataclass
class Melody:
	name: str
	points: int
	file: Any
	is_guessed: bool
	category: Category
