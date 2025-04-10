import time
from datetime import timedelta

from default_category import DefaultCategory
from default_melody import DefaultMelody
from default_player import DefaultPlayer
from guess_the_melody_game import GuessTheMelodyGame

players = [DefaultPlayer('Alex'), DefaultPlayer('John')]
categories = [
    DefaultCategory('Шансон', [
        DefaultMelody('Михаил Круг - Владимирский централ', 'Михаил Круг - Владимирский централ', 100)
    ])
]
game = GuessTheMelodyGame(players, categories, listening_time=timedelta(seconds=5))

game.pick_melody(game.choosing_player, game.get_not_guessed_melodies()[game.categories[0]][0])
game.answer(game.players[0], '123')
game.reject_answer()
print()
