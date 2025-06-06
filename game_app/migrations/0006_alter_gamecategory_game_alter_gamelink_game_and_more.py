# Generated by Django 5.1.7 on 2025-04-11 13:21

import datetime
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
	dependencies = [
		('game_app', '0005_alter_gamestate_last_action_alter_gamestate_state'),
	]

	operations = [
		migrations.AlterField(
			model_name='gamecategory',
			name='game',
			field=models.ForeignKey(
				on_delete=django.db.models.deletion.CASCADE,
				related_name='categories',
				to='game_app.guessthemelodygame',
			),
		),
		migrations.AlterField(
			model_name='gamelink',
			name='game',
			field=models.ForeignKey(
				on_delete=django.db.models.deletion.CASCADE,
				related_name='links',
				to='game_app.guessthemelodygame',
			),
		),
		migrations.AlterField(
			model_name='gamestate',
			name='game',
			field=models.OneToOneField(
				on_delete=django.db.models.deletion.CASCADE,
				related_name='state',
				to='game_app.guessthemelodygame',
			),
		),
		migrations.AlterField(
			model_name='gamestate',
			name='last_action',
			field=models.DateTimeField(
				db_default=datetime.datetime(2025, 4, 11, 18, 21, 37, 774860),
				default=datetime.datetime(2025, 4, 11, 18, 21, 37, 774860),
			),
		),
		migrations.AlterField(
			model_name='melody',
			name='game_category',
			field=models.ForeignKey(
				on_delete=django.db.models.deletion.CASCADE,
				related_name='melodies',
				to='game_app.gamecategory',
			),
		),
		migrations.AlterField(
			model_name='player',
			name='game',
			field=models.ForeignKey(
				on_delete=django.db.models.deletion.DO_NOTHING,
				related_name='players',
				to='game_app.guessthemelodygame',
			),
		),
	]
