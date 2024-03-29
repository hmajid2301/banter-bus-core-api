import base64
from datetime import datetime

import factory
import factory.fuzzy

from app.game_state.game_state_models import (
    FibbingActions,
    GamePaused,
    GameState,
    PlayerScore,
)
from app.player.player_models import NewPlayer, Player
from app.room.room_models import Room, RoomState
from tests.unit.data.data import starting_state

game_names = ["quibly", "fibbing_it", "drawlosseum"]


class PlayerFactory(factory.Factory):
    class Meta:
        model = Player

    player_id = factory.Faker("uuid4")
    avatar = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
    )
    nickname = factory.Faker("first_name")
    room_id = factory.Faker("uuid4")
    latest_sid = factory.Faker(
        "lexify", text="??????????????", letters="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    )
    disconnected_at = None


class RoomFactory(factory.Factory):
    class Meta:
        model = Room

    room_id = factory.Faker("uuid4")
    game_name = None
    host = None
    state = factory.fuzzy.FuzzyChoice(RoomState)
    created_at = datetime.now()
    updated_at = datetime.now()
    players = factory.List([factory.SubFactory(PlayerFactory)])


class GameStateFactory(factory.Factory):
    class Meta:
        model = GameState

    state = starting_state
    game_name = factory.fuzzy.FuzzyChoice(game_names)
    room_id = factory.Faker("uuid4")
    player_scores: list[PlayerScore] = []
    action = FibbingActions.show_question  # Fix this use action depending on game
    paused = GamePaused()
    action_completed_by = None


def get_new_player() -> NewPlayer:
    player: Player = PlayerFactory.build()
    return NewPlayer(**player.dict())
