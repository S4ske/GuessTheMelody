from datetime import datetime

from django.contrib.postgres.fields import ArrayField
from django.db import models


class GuessTheMelodyGame(models.Model):
    invite_code = models.CharField(max_length=6, unique=True)

    def __str__(self):
        return self.pk


class GameState(models.Model):
    class States(models.TextChoices):
        CREATED = 'created'
        CHOOSING = 'choosing'
        LISTENING = 'listening'
        ANSWERING = 'answering'
        FINISHED = 'finished'

    game = models.ForeignKey(GuessTheMelodyGame, on_delete=models.CASCADE, unique=True)
    state = models.CharField(choices=States.choices, max_length=255)
    time_left = models.IntegerField(default=None, db_default=None, null=True, blank=True)
    end_time = models.DateTimeField(default=None, db_default=None, null=True, blank=True)
    start_time = models.DateTimeField(default=None, db_default=None, null=True, blank=True)
    current_melody_id = models.IntegerField(default=None, db_default=None, null=True, blank=True)
    choosing_player_id = models.IntegerField(default=None, db_default=None, null=True, blank=True)
    answering_player_id = models.IntegerField(default=None, db_default=None, null=True, blank=True)
    answer = models.CharField(max_length=255, default=None, db_default=None, null=True, blank=True)  # noqa: DJ001
    last_action = models.DateTimeField(default=datetime.now(), db_default=datetime.now())
    delete_at = models.DateTimeField(default=None, db_default=None, null=True, blank=True)
    answered_players_ids = ArrayField(models.IntegerField(), null=True, blank=True, default=None, db_default=None)

    def __str__(self):
        return self.state


class Player(models.Model):
    points = models.IntegerField(default=0, db_default=0)
    game = models.ForeignKey(GuessTheMelodyGame, on_delete=models.DO_NOTHING)
    nickname = models.CharField(max_length=255)
    is_master = models.BooleanField(default=False, db_default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['game', 'nickname'],
                name='unique_game_nickname'
            )
        ]

    def __str__(self):
        return str(self.points)


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class GameCategory(models.Model):
    game = models.ForeignKey(GuessTheMelodyGame, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.RESTRICT)

    def __str__(self):
        return self.game


class Melody(models.Model):
    game_category = models.ForeignKey(GameCategory, on_delete=models.CASCADE)
    points = models.IntegerField(default=0, db_default=0)
    name = models.CharField(max_length=255)
    link = models.CharField(max_length=255)
    is_guessed = models.BooleanField(default=False, db_default=False)

    def __str__(self):
        return self.points


class GameLink(models.Model):
    link = models.CharField(max_length=255)
    game = models.ForeignKey(GuessTheMelodyGame, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE, unique=True)

    def __str__(self):
        return self.link
