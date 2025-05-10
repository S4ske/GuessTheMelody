import random
import re
import threading

from yandex_music import Client, Track

from game_app.config import YANDEX_MUSIC_TOKEN

yandex_client = Client(YANDEX_MUSIC_TOKEN).init()

playlists_re = re.compile(r'https://.+yandex.+/playlists/(?P<playlist_id>.+)(\?.+)?')
default_genres = {'баста', 'король и шут', 'feduk', 'miyagi', 'элджей'}


def check_album(link: str) -> bool:
	return playlists_re.match(link) is not None


def get_playlist(link, playlists, lock, playlists_re):
	match_obj = playlists_re.match(link)
	if not match_obj:
		return
	playlist = yandex_client.users_playlists(match_obj.group('playlist_id'), match_obj.group('user_id'))
	with lock:
		playlists.append(playlist)


def check_genre(genre, lock, all_genres, bad):
	if not yandex_client.search(genre, type_='track', nocorrect=True).tracks and genre in all_genres:
		with lock:
			bad[0] = True
			all_genres.remove(genre)


def resolve_genre(genre, all_tracks: list, all_tracks_ids: set, result: dict[str, list],
				  all_tracks_ids_lock: threading.Lock):
	melodies_by_genre = list(filter(lambda x: get_genre(x) == genre, all_tracks))
	if len(melodies_by_genre) <= 5:
		result[genre] = melodies_by_genre

		last_tracks = melodies_by_genre
		while len(result[genre]) < 5:
			new_melodies_by_genre = []
			for track in last_tracks:
				for new_track in yandex_client.tracks_similar(track.id).similar_tracks:
					if new_track.id in all_tracks_ids:
						continue
					with all_tracks_ids_lock:
						all_tracks_ids.add(new_track.id)
					new_melodies_by_genre.append(new_track)
			if not new_melodies_by_genre:
				if len(last_tracks) > 0:
					for old_track in last_tracks:
						for artist in old_track.artists:
							artist_tracks = artist.get_tracks().tracks
							for artist_track in artist_tracks:
								if artist_track.id in all_tracks_ids:
									continue
								with all_tracks_ids_lock:
									all_tracks_ids.add(artist_track.id)
								new_melodies_by_genre.append(artist_track)
				else:
					new_melodies_by_genre = yandex_client.search(genre, type_='track', nocorrect=True).tracks.results
			if len(new_melodies_by_genre) >= 5 - len(result[genre]):
				result[genre].extend(random.sample(new_melodies_by_genre, 5 - len(result[genre])))
			else:
				result[genre].extend(new_melodies_by_genre)
				last_tracks = new_melodies_by_genre
	else:
		result[genre] = random.sample(melodies_by_genre, 5)


def get_similar(track, all_tracks, all_tracks_ids, similar_lock):
	for more_track in yandex_client.tracks_similar(track.id).similar_tracks:
		if more_track.id in all_tracks_ids:
			continue
		with similar_lock:
			all_tracks.append(more_track)
			all_tracks_ids.add(more_track.id)


def mix_albums(links: list[str]) -> dict[str, list[Track]]:
	playlists_lock = threading.Lock()
	playlists = []

	all_tracks: list[Track] = []
	all_tracks_ids = set()

	threads_pool = [
		threading.Thread(target=get_playlist, args=(link, playlists, playlists_lock, playlists_re)) for link in links
	]
	for thread in threads_pool:
		thread.start()

	for thread in threads_pool:
		thread.join()

	for playlist in playlists:
		for track_short in playlist.tracks:
			if track_short.id in all_tracks_ids:
				continue
			all_tracks_ids.add(track_short.id)
			all_tracks.append(track_short.track)

	threads_pool = []
	similar_lock = threading.Lock()
	for track in random.sample(all_tracks, min(7, len(all_tracks))):
		thread = threading.Thread(target=get_similar, args=(track, all_tracks, all_tracks_ids, similar_lock))
		threads_pool.append(thread)
		thread.start()

	for thread in threads_pool:
		thread.join()

	all_genres = extract_genres(all_tracks)
	all_genres = sorted(all_genres, key=lambda x: len(list(filter(lambda y: get_genre(y) == x, all_tracks))),
						reverse=True)
	all_genres = all_genres[:min(len(all_genres), 7)]
	bad_lock = threading.Lock()
	bad = [False]

	while True:
		if len(all_genres) >= 5:
			genres = random.sample(list(all_genres), 5)
		else:
			genres = list(all_genres)
			genres.extend(random.sample(list(default_genres.difference(all_genres)), 5 - len(all_genres)))
		bad = [False]
		# threads_pool = []
		# for genre in genres:
		#     thread = threading.Thread(target=check_genre, args=(genre, bad_lock, all_genres, bad))
		#     threads_pool.append(thread)
		#     thread.start()
		# for thread in threads_pool:
		#     thread.join()
		if not bad[0]:
			break

	all_tracks = list(filter(lambda x: get_genre(x) in genres, all_tracks))

	result = {}
	all_tracks_ids_lock = threading.Lock()
	threads_pool = []
	for genre in genres:
		thread = threading.Thread(
			target=resolve_genre, args=(genre, all_tracks, all_tracks_ids, result, all_tracks_ids_lock)
		)
		threads_pool.append(thread)
		thread.start()

	for thread in threads_pool:
		thread.join()

	return result


def extract_genres(tracks: list[Track]) -> set[str]:
	res = set()
	for track in tracks:
		res.add(get_genre(track))
	return res


def get_genre(track: Track) -> str:
	meta = track.meta_data
	if meta is None:
		return track.albums[0].genre
	else:
		return meta.genre
