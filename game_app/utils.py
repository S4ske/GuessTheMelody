import random
import string

from jwt import decode, encode

from domain import AnswerCheckState, GuessTheMelodyGame, IsFinishedState, MelodyListeningState, MelodyPickState
from game_app.domain_wrappers import CategoriesProvider, PlayersProvider, StateInfoProvider
from game_app.models import GuessTheMelodyGame as GuessTheMelodyGameDB

from .config import JWT_ALGORITHM, JWT_SECRET_KEY


class GameIsNotStartedError(Exception):
	pass


def get_game_from_db(game_id: int) -> GuessTheMelodyGame:
	game_db = GuessTheMelodyGameDB.objects.prefetch_related(
		'state',
		'players'
	).get(pk=game_id)
	state_db = game_db.state
	game = GuessTheMelodyGame(
		categories_provider=CategoriesProvider(game_id),
		players_provider=PlayersProvider(game_id),
		state_info_provider=StateInfoProvider(game_id)
	)
	state = None
	match state_db.state:
		case 'created':
			raise GameIsNotStartedError()
		case 'choosing':
			state = MelodyPickState(game)
		case 'listening':
			state = MelodyListeningState(game)
		case 'answering':
			state = AnswerCheckState(game)
		case 'finished':
			state = IsFinishedState(game)
	game.set_state(state)
	return game


def get_jwt_token(payload: dict) -> str:
	return encode(payload, algorithm=JWT_ALGORITHM, key=JWT_SECRET_KEY)


def decode_jwt_token(token: str) -> dict:
	return decode(token, algorithms=[JWT_ALGORITHM], key=JWT_SECRET_KEY)


def generate_random_string(length=6):
	characters = string.ascii_uppercase + string.digits
	return ''.join(random.choice(characters) for _ in range(length))
