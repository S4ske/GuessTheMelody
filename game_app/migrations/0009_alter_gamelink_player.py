# Generated by Django 5.1.7 on 2025-04-16 17:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
	dependencies = [
		('game_app', '0008_remove_gamestate_last_action'),
	]

	operations = [
		migrations.AlterField(
			model_name='gamelink',
			name='player',
			field=models.OneToOneField(
				null=True,
				on_delete=django.db.models.deletion.CASCADE,
				related_name='link',
				to='game_app.player',
			),
		),
	]
