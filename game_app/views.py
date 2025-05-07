import os

from asgiref.sync import async_to_sync
from channels.layers import BaseChannelLayer, get_channel_layer
from django.db import IntegrityError
from django.http import FileResponse, HttpRequest, HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from .models import GameLink, GameState, GuessTheMelodyGame, Player
from .utils import decode_jwt_token, generate_random_string, get_jwt_token
from .yandex_client import check_album


def create_game_db() -> GuessTheMelodyGame:
	while True:
		try:
			return GuessTheMelodyGame(invite_code=generate_random_string())
		except IntegrityError:
			continue


def create_game(request: HttpRequest, nickname: str) -> HttpResponse:
	game = create_game_db()
	game.save()

	GameState.objects.create(game=game, state=GameState.States.CREATED)
	Player.objects.create(game=game, nickname=nickname, is_master=True)

	response = HttpResponse(game.invite_code)
	response.set_cookie(
		'game_token',
		get_jwt_token(
			{
				'nickname': nickname,
				'game_id': str(game.pk),
			},
		),  # TODO: поменять samesite
		httponly=True,
		samesite='None',
		secure=True,
	)

	return response


def get_token(request: HttpRequest) -> HttpResponse:
	nickname = request.GET.get('nickname')
	invite_code = request.GET.get('invite_code')
	if not nickname or not invite_code:
		return HttpResponseBadRequest('Отсутвует query параметр "nickname" или "invite_code"')

	game = get_object_or_404(GuessTheMelodyGame, invite_code=invite_code)
	player = game.players.filter(nickname=nickname)
	if player:
		return HttpResponseBadRequest('В игре уже есть игрок с таким никнеймом')
	response = HttpResponse()
	response.set_cookie(
		'game_token',
		get_jwt_token(
			{
				'nickname': nickname,
				'game_id': str(game.pk),
			},
		),  # TODO: поменять samesite
		httponly=True,
		samesite='None',
		secure=True,
	)
	player = Player(game=game, nickname=nickname)

	channel_layer: BaseChannelLayer = get_channel_layer()
	async_to_sync(channel_layer.group_send)(
		str(game.pk),
		{
			'type': 'new_player',
			'payload': {
				'nickname': nickname,
				'points': player.points,
				'is_master': player.is_master,
				'game_id': str(game.pk),
			},
		},
	)

	player.save()
	return response


def delete_token(request: HttpRequest) -> HttpResponse:
	token = request.COOKIES.get('game_token')
	if not token:
		return HttpResponseBadRequest('Пользователь не авторизован')
	token = decode_jwt_token(token)
	nickname = token['nickname']
	game_id = int(token['game_id'])
	if not nickname or not game_id:
		return HttpResponseBadRequest()
	game = get_object_or_404(GuessTheMelodyGame, pk=game_id)
	player = game.players.get(nickname=nickname)
	player.delete()
	player.save()
	response = HttpResponse()
	response.delete_cookie('game_token')
	return response


@csrf_exempt
def add_link(request: HttpRequest) -> HttpResponse:
	link = request.body
	if not link:
		return HttpResponseBadRequest('Нет ссылки')
	link = link.decode()
	token = request.COOKIES.get('game_token')
	if not token:
		return HttpResponseBadRequest('Пользователь не авторизован')
	token = decode_jwt_token(token)
	nickname = token['nickname']
	game_id = int(token['game_id'])
	if not nickname or not game_id:
		return HttpResponseBadRequest('Что-то не так с токеном')
	if not check_album(link):
		return HttpResponseBadRequest('Плохая ссылка')
	game = get_object_or_404(GuessTheMelodyGame, pk=game_id)
	player = game.players.get(nickname=nickname)
	link_db = GameLink(game=game, player=player, link=link)
	link_db.save()
	return HttpResponse('success')


def get_melody_file(request: HttpRequest, filename: str) -> HttpResponseBadRequest | FileResponse:
	filename = f'{filename}.mp3'
	filepath = os.path.join('game_app', 'tracks_files', filename)

	file = open(filepath, 'rb')

	response = FileResponse(
		file,
		content_type='audio/mpeg',
		as_attachment=False
	)

	response['Content-Disposition'] = f'inline; filename="{os.path.basename(filepath)}"'

	response._resource_closers.append(file.close)

	return response
