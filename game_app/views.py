from django.db import IntegrityError
from django.http import HttpRequest, HttpResponse

from .models import GameState, GuessTheMelodyGame, Player
from .utils import generate_random_string


def create_game_db(invite_code: str) -> GuessTheMelodyGame:
    while True:
        try:
            return GuessTheMelodyGame(invite_code=invite_code)
        except IntegrityError:
            continue


def create_game(request: HttpRequest, nickname: str) -> HttpResponse:
    invite_code = generate_random_string()

    game = create_game_db(invite_code)
    game.save()

    GameState.objects.create(game=game, state=GameState.States.CREATED)
    Player.objects.create(game=game, nickname=nickname, is_master=True)

    return HttpResponse(invite_code)
