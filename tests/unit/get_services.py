from app.clients.management_api.api.games_api import AsyncGamesApi
from app.clients.management_api.api.questions_api import AsyncQuestionsApi
from app.clients.management_api.api_client import ApiClient
from app.game_state.game_state_models import GameState
from app.game_state.game_state_service import GameStateService
from app.game_state.games.fibbing_it.fibbing_it import FibbingIt
from app.player.player_service import PlayerService
from app.room.lobby.lobby_service import LobbyService
from app.room.room_models import Room
from app.room.room_service import RoomService
from tests.unit.factories import GameStateFactory, RoomFactory
from tests.unit.game_state.fake_game_state_repository import FakeGameStateRepository
from tests.unit.room.fake_room_repository import FakeRoomRepository


def get_player_service(rooms: list[Room] | None = None, num: int = 1, **kwargs) -> PlayerService:
    if rooms:
        existing_room = rooms
    elif num:
        existing_room = RoomFactory.build_batch(num, **kwargs)
    else:
        existing_room = []

    room_repository = FakeRoomRepository(rooms=existing_room)
    return PlayerService(room_repository=room_repository)


def get_room_service(rooms: list[Room] | None = None, num: int = 1, **kwargs) -> RoomService:
    if rooms:
        existing_room = rooms
    elif num:
        existing_room = RoomFactory.build_batch(num, **kwargs)
    else:
        existing_room = []

    room_repository = FakeRoomRepository(rooms=existing_room)
    return RoomService(room_repository=room_repository)


def get_lobby_service(
    rooms: list[Room] | None = None, num: int = 1, game_states: list[GameState] | None = None, **kwargs
) -> LobbyService:
    room_service = get_room_service(rooms=rooms, num=num, **kwargs)
    player_service = get_player_service(rooms=rooms, num=num, **kwargs)
    game_state_service = get_game_state_service(game_states=game_states)
    return LobbyService(room_service=room_service, player_service=player_service, game_state_service=game_state_service)


def get_game_state_service(game_states: list[GameState] | None = None, num: int = 1, **kwargs) -> GameStateService:
    if game_states:
        existing_game_states = game_states
    elif num:
        existing_game_states = GameStateFactory.build_batch(num, **kwargs)
    else:
        existing_game_states = []

    question_client = get_question_api_client()
    game_state_repository = FakeGameStateRepository(game_states=existing_game_states)
    return GameStateService(game_state_repository=game_state_repository, question_client=question_client)


def get_game_api_client() -> AsyncGamesApi:
    api_client = ApiClient(host="http://localhost")
    return AsyncGamesApi(api_client=api_client)


def get_question_api_client() -> AsyncQuestionsApi:
    api_client = ApiClient(host="http://localhost")
    return AsyncQuestionsApi(api_client=api_client)


def get_fibbing_it_game() -> FibbingIt:
    return FibbingIt()
