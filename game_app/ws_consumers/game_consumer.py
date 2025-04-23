import re
import threading
from typing import Callable

from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer
from yandex_music import Track

from domain import AlreadyPickedError, PlayerAlreadyAnsweredError, StateError, WrongPlayerChoosingError

from ..models import Category, GameState, GuessTheMelodyGame, Melody, Player
from ..utils import GameIsNotStartedError, decode_jwt_token, get_game_from_db
from ..yandex_client import mix_albums


def wrap_errors(func: Callable[['GameConsumer', ...], ...]):
	def wrapper(self: 'GameConsumer', *args, **kwargs):
		try:
			func(self, *args, **kwargs)
		except GameIsNotStartedError:
			self.send_exception('Game is not started')
		except StateError:
			self.send_exception('This action is not available in the current state')
		except WrongPlayerChoosingError:
			self.send_exception('Now another player chooses')
		except PlayerAlreadyAnsweredError:
			self.send_exception('Some player has already answered')
		except AlreadyPickedError:
			self.send_exception('This song has been chosen before')

	return wrapper


def master_action(func: Callable[['GameConsumer', ...], ...]):
	def wrapper(self: 'GameConsumer', *args, **kwargs):
		if not Player.objects.get(nickname=self.nickname, game__pk=self.game_id).is_master:
			self.send_exception('User must be a master')
		else:
			func(self, *args, **kwargs)

	return wrapper


class GameConsumer(JsonWebsocketConsumer):
	player_id: int
	nickname: str
	game_id: int
	
	def send_exception(self, message: str) -> None:
		self.send_json({
			'type': 'exception',
			'payload': {
				'message': message
			}
		})

	def connect(self) -> None:
		headers = self.scope["headers"]
		print(headers)
		cookies = list(filter(lambda x: x[0] == b'cookie', headers))
		print('123123123123123' + cookies[0][1].decode())
		if not cookies:
			self.close()
			return

		token_match = re.match(r'.*game_token=([^;]+).*', cookies[0][1].decode())
		print('123123123123123' + token_match.group(1))
		if not token_match:
			self.close()
			return
		token = decode_jwt_token(token_match.group(1))
		print(token)
		game_id = int(token.get('game_id'))
		if not game_id:
			self.close()
			return

		game = GuessTheMelodyGame.objects.select_related('state').prefetch_related('categories', 'players').get(pk=game_id)
		if not game:
			self.close()
			return
		self.game_id = game.pk

		self.nickname = token.get('nickname')
		if not self.nickname:
			self.close()
			return

		player = Player.objects.get(nickname=self.nickname, game=game)
		self.player_id = player.pk
		if not self.player_id:
			self.close()
			return

		game_state = game.state
		players = game.players.prefetch_related('link').all()
		print(players)

		response = {
			'type': 'init',
			'payload': {
				'invite_code': game.invite_code,
				'current_player_nickname': self.nickname,
				'state_info': {
					'state': game_state.state,
					'time_left': game_state.time_left,
					'end_time': game_state.end_time.isoformat() if game_state.end_time else None,
					'start_time': game_state.start_time.isoformat() if game_state.start_time else None,
					'current_melody_id': game_state.current_melody_id,
					'choosing_player_id': game_state.choosing_player_id,
					'answering_player_id': game_state.answering_player_id,
					'answer': game_state.answer,
					'answered_players_ids': game_state.answered_players_ids,
				},
				'players': [
					{
						'id': player.pk,
						'nickname': player.nickname,
						'points': player.points,
						'is_master': player.is_master,
						'link': getattr(player, 'link', None).link if getattr(player, 'link', None) else None,
					}
					for player in players
				],
				'categories': [
					{
						'category_name': category.name,
						'melodies': [
							{
								'points': melody.points,
								'name': melody.name,
								'link': melody.link,
								'is_guessed': melody.is_guessed,
							}
							for melody in category.melodies.all()
						],
					}
					for category in game.categories.prefetch_related('melodies').all()
				],
			},
		}

		async_to_sync(self.channel_layer.group_add)(str(self.game_id), self.channel_name)
		self.accept()
		self.send_json(response)

	def disconnect(self, code):
		if hasattr(self, 'game_id'):
			async_to_sync(self.channel_layer.group_discard)(str(self.game_id), self.channel_name)
		self.close()

	@wrap_errors
	def handle_pick_melody(self, content: dict):
		game = get_game_from_db(self.game_id)
		payload = content['payload']

		game.pick_melody(self.nickname, payload['category'], int(payload['points']))
		melody = game.current_melody

		async_to_sync(self.channel_layer.group_send)(
			str(self.game_id),
			{
				'type': 'pick_melody',
				'payload': {
					'start_time': game.start_time.isoformat() if game.start_time else None,
					'end_time': game.end_time.isoformat() if game.end_time else None,
					'category_name': melody.category.name,
					'melody_name': melody.name,
					'points': melody.points,
					'link': melody.file,
					'answered_players_nicknames': list(map(lambda x: x.nickname, game.already_answered_players)),
				},
			},
		)

	@wrap_errors
	def handle_answer(self, content: dict):
		game = get_game_from_db(self.game_id)
		answer = content['payload']['answer']
		game.answer(self.nickname, answer)
		melody = game.current_melody

		async_to_sync(self.channel_layer.group_send)(
			str(self.game_id),
			{
				'type': 'answer',
				'payload': {
					'answering_player_nickname': self.nickname,
					'answer': answer,
					'category_name': melody.category.name,
					'melody_name': melody.name,
					'points': melody.points,
					'link': melody.file,
				},
			},
		)

	@master_action
	@wrap_errors
	def handle_accept_answer_partially(self, content: dict):
		game = get_game_from_db(self.game_id)
		game.accept_answer_partially()
		melody = game.current_melody

		async_to_sync(self.channel_layer.group_send)(
			str(self.game_id),
			{
				'type': 'accept_answer_partially',
				'payload': {
					'start_time': game.start_time.isoformat() if game.start_time else None,
					'end_time': game.end_time.isoformat() if game.end_time else None,
					'choosing_player': game.choosing_player.nickname,
					'melody_name': melody.name,
					'category_name': melody.category.name,
					'points': melody.points,
					'link': melody.file,
					'answered_players_nicknames': list(map(lambda x: x.nickname, game.already_answered_players)),
				},
			},
		)

	@master_action
	@wrap_errors
	def handle_accept_answer(self, content: dict):
		game = get_game_from_db(self.game_id)
		game.accept_answer()

		async_to_sync(self.channel_layer.group_send)(
			str(self.game_id),
			{
				'type': 'accept_answer',
				'payload': {
					'choosing_player': game.choosing_player.nickname,
				},
			},
		)

	@master_action
	@wrap_errors
	def handle_reject_answer(self, content: dict):
		game = get_game_from_db(self.game_id)
		game.reject_answer()
		melody = game.current_melody

		async_to_sync(self.channel_layer.group_send)(
			str(self.game_id),
			{
				'type': 'accept_answer',
				'payload': {
					'start_time': game.start_time.isoformat() if game.start_time else None,
					'end_time': game.end_time.isoformat() if game.end_time else None,
					'choosing_player': game.choosing_player.nickname,
					'melody_name': melody.name,
					'category_name': melody.category.name,
					'points': melody.points,
					'link': melody.file,
					'answered_players_nicknames': list(map(lambda x: x.nickname, game.already_answered_players)),
				},
			},
		)

	@master_action
	def handle_transfer_master(self, content: dict):
		master = Player.objects.get(game__pk=self.game_id, is_master=True)
		master.is_master = False

		try:
			player = Player.objects.get(game__pk=self.game_id, nickname=content['payload']['nickname'])
		except Player.DoesNotExist:
			self.send_exception('There is no player with this nickname')
			return
		player.is_master = True
		
		nickname = content['payload']['nickname']
		
		master.save()
		player.save()

		async_to_sync(self.channel_layer.group_send)(
			str(self.game_id),
			{
				'type': 'transfer_master',
				'payload': {
					'nickname': nickname,
				},
			},
		)
	
	def _handle_melody(self, melody: Track, category_db: Category, points: int):
		available_qualities = melody.get_download_info()
		if not available_qualities:
			self.send_exception('The track is not available for download')
			return

		best_quality = max(available_qualities,
						   key=lambda x: int(x.bitrate_in_kbps) if x.bitrate_in_kbps else 0)

		download_url = best_quality.get_direct_link()
		if not download_url:
			self.send_exception('Failed to get download link')
			return
		melody_db = Melody(
			category=category_db,
			points=points,
			name=melody.title + ' ' + ' '.join(melody.artists_name()),
			link=download_url,
		)
		melody_db.save()

	def _start_game(self, game):
		links = list(map(lambda x: x.link, game.links.all()))
		categories = mix_albums(links)
		threads = []
		for category, melodies in categories.items():
			category_db = Category(game=game, name=category)
			category_db.save()
			for i in range(1, len(melodies) + 1):
				thread = threading.Thread(target=self._handle_melody, args=(melodies[i - 1], category_db, 100 * i))
				thread.start()
				threads.append(thread)
		for thread in threads:
			thread.join()
		game_state_prev = GameState.objects.get(game__pk=self.game_id)
		game_state = GameState(
			game=game, state='choosing', choosing_player_id=game.players.filter(is_master=False).first().pk
		)
		game_state_prev.delete()
		game_state.save()

	@master_action
	def handle_start_game(self, content: dict):
		game = GuessTheMelodyGame.objects.get(pk=self.game_id)

		if game.state.state != 'created':
			self.send_exception('The game has already begun')
			return

		if game.links.count() < 1:
			self.send_exception('At least one player must load the playlist to start the game')
			return

		if game.players.count() < 2:
			self.send_exception('There must be at least two players in the game')
			return

		self._start_game(game)
		
		game_state = game.state

		async_to_sync(self.channel_layer.group_send)(
			str(self.game_id),
			{
				'type': 'start_game',
				'payload': {
					'state_info': {
						'state': game_state.state,
						'time_left': game_state.time_left,
						'end_time': game_state.end_time.isoformat() if game_state.end_time else None,
						'start_time': game_state.start_time.isoformat() if game_state.start_time else None,
						'current_melody_id': game_state.current_melody_id,
						'choosing_player_id': game_state.choosing_player_id,
						'answering_player_id': game_state.answering_player_id,
						'answer': game_state.answer,
						'delete_at': game_state.delete_at,
						'answered_players_ids': game_state.answered_players_ids,
					},
					'categories': [
						{
							'category_name': category.name,
							'melodies': [
								{
									'points': melody.points,
									'name': melody.name,
									'link': melody.link,
									'is_guessed': melody.is_guessed,
								}
								for melody in category.melodies.all()
							],
						}
						for category in game.categories.all()
					],
				},
			},
		)
	
	def new_player(self, content):
		self.send_json(content)

	def transfer_master(self, content):
		self.send_json(content)
		
	def start_game(self, content):
		self.send_json(content)
		
	def pick_melody(self, content):
		self.send_json(content)
		
	def answer(self, content):
		self.send_json(content)
		
	def accept_answer_partially(self, content):
		self.send_json(content)
		
	def accept_answer(self, content):
		self.send_json(content)
		
	def reject_answer(self, content):
		self.send_json(content)

	def receive_json(self, content, **kwargs):
		match content['type']:
			case 'transfer_master':
				self.handle_transfer_master(content)
			case 'start_game':
				self.handle_start_game(content)
			case 'pick_melody':
				self.handle_pick_melody(content)
			case 'answer':
				self.handle_answer(content)
			case 'accept_answer_partially':
				self.handle_accept_answer_partially(content)
			case 'accept_answer':
				self.handle_accept_answer(content)
			case 'reject_answer':
				self.handle_reject_answer(content)
			case _:
				self.send_exception('Unknown command')
