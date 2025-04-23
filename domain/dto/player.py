from dataclasses import dataclass


@dataclass
class Player:
	nickname: str
	is_master: bool
	points: int
