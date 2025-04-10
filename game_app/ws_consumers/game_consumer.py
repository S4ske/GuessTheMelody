from channels.generic.websocket import AsyncJsonWebsocketConsumer

from ..models import GuessTheMelodyGame


class GameConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        invite_code = self.scope['url_route']['kwargs']['invite_code']
        self.game_id = GuessTheMelodyGame.objects.get(invite_code=invite_code).id
        await self.channel_layer.group_add(
            self.game_id,
            self.channel_name
        )
        await self.accept()
        await self.channel_layer.group_send({})  # TODO: Сделать

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.game_id,
            self.channel_name
        )

    async def receive_json(self, content, **kwargs):
        match content['event_type']:
            case _:
                pass
