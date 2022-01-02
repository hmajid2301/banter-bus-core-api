import base64
from datetime import datetime

import factory
import factory.fuzzy

from app.player.player_models import NewPlayer, Player
from app.room.room_models import Room, RoomState

game_names = ["quibly", "fibbing_it", "drawlosseum"]


class RoomFactory(factory.Factory):
    class Meta:
        model = Room

    room_id = factory.Faker("uuid4")
    game_name = factory.fuzzy.FuzzyChoice(game_names)
    room_code = factory.Faker("lexify", text="?????", letters="ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    host = None
    state = factory.fuzzy.FuzzyChoice(RoomState)
    created_at = datetime.now()
    updated_at = datetime.now()


class PlayerFactory(factory.Factory):
    class Meta:
        model = Player

    player_id = factory.Faker("uuid4")
    avatar = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
    )
    nickname = factory.Faker("first_name")
    room_id = factory.Faker("uuid4")


def get_new_player() -> NewPlayer:
    player: Player = PlayerFactory.build()
    new_player = NewPlayer(**player.dict())
    return new_player
