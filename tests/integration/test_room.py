import asyncio
from datetime import datetime, timedelta

import pytest
from socketio.asyncio_client import AsyncClient

from app.event_models import Error
from app.game_state.game_state_factory import get_game_state_service
from app.game_state.game_state_models import FibbingActions
from app.main import sio
from app.player.player_factory import get_player_service
from app.room.room_events_models import (
    AnswerSubmittedFibbingIt,
    GamePaused,
    GameUnpaused,
    GetNextQuestion,
    GotNextQuestion,
    HostDisconnected,
    PauseGame,
    PlayerDisconnected,
    RejoinRoom,
    SubmitAnswerFibbingIt,
    UnpauseGame,
)
from tests.integration.conftest import BASE_URL


@pytest.mark.asyncio
async def test_rejoin_room_that_has_started(client: AsyncClient):
    future = asyncio.get_running_loop().create_future()
    player_id = "8cdc1984-e832-48c7-9d89-1d724665bef1"
    player_service = get_player_service()
    player = await player_service.get(player_id=player_id)
    await player_service.update_latest_sid(latest_sid=client.get_sid(), player=player)

    @client.on("GOT_NEXT_QUESTION")
    def _(data):
        future.set_result(GotNextQuestion(**data))

    rejoin_room = RejoinRoom(player_id=player_id)
    await client.emit("REJOIN_ROOM", rejoin_room.dict())
    await asyncio.wait_for(future, timeout=5.0)

    got_next_question: GotNextQuestion = future.result()
    assert got_next_question.updated_round.round_changed is True
    assert got_next_question.updated_round.new_round == "opinion"
    assert got_next_question.question.answers is not None  # type: ignore


@pytest.mark.asyncio
async def test_rejoin_room_game_unpaused(client: AsyncClient):
    future = asyncio.get_running_loop().create_future()
    player_id = "8cdc1984-e832-48c7-9d89-1d724665bef1"
    player_service = get_player_service()
    player = await player_service.get(player_id=player_id)
    await player_service.update_latest_sid(latest_sid=client.get_sid(), player=player)

    game_state_service = get_game_state_service()
    await game_state_service.pause_game(room_id="2257856e-bf37-4cc4-8551-0b1ccdc38c60", player_disconnected=player_id)

    @client.on("GAME_UNPAUSED")
    def _(data):
        future.set_result(GameUnpaused())

    rejoin_room = RejoinRoom(player_id=player_id)
    await client.emit("REJOIN_ROOM", rejoin_room.dict())
    await asyncio.wait_for(future, timeout=5.0)
    game_unpaused: GameUnpaused = future.result()
    assert game_unpaused


@pytest.mark.asyncio
async def test_rejoin_room_game_should_not_unpaused(client: AsyncClient):
    future = asyncio.get_running_loop().create_future()
    player_id = "8cdc1984-e832-48c7-9d89-1d724665bef1"
    player_service = get_player_service()
    player = await player_service.get(player_id=player_id)
    await player_service.update_latest_sid(latest_sid=client.get_sid(), player=player)

    game_state_service = get_game_state_service()
    await game_state_service.pause_game(room_id="2257856e-bf37-4cc4-8551-0b1ccdc38c60", player_disconnected=player_id)
    await game_state_service.pause_game(
        room_id="2257856e-bf37-4cc4-8551-0b1ccdc38c60", player_disconnected="99acb730-93de-4364-917a-8760ee50d0gg"
    )

    @client.on("GAME_UNPAUSED")
    def _(data):
        future.set_result(GameUnpaused())

    rejoin_room = RejoinRoom(player_id=player_id)
    await client.emit("REJOIN_ROOM", rejoin_room.dict())

    with pytest.raises(asyncio.exceptions.TimeoutError):
        await asyncio.wait_for(future, timeout=1.0)


@pytest.mark.asyncio
async def test_disconnect(client: AsyncClient, client_two: AsyncClient):
    future = asyncio.get_running_loop().create_future()
    player_service = get_player_service()
    player = await player_service.get(player_id="778cb730-93de-4364-917a-8760ee50d0ff")
    sio.enter_room(client_two.get_sid(), room=player.room_id)
    await player_service.update_latest_sid(player=player, latest_sid=client.get_sid())

    @client_two.on("PLAYER_DISCONNECTED")
    def _(data):
        future.set_result(PlayerDisconnected(**data))

    await client.disconnect()
    await asyncio.wait_for(future, timeout=5.0)

    player_disconnected_nickname = player.nickname
    player_disconnected: PlayerDisconnected = future.result()
    assert player_disconnected.nickname == player_disconnected_nickname
    sio.leave_room(client_two.get_sid(), room=player.room_id)
    await client.connect(BASE_URL, socketio_path="/ws/socket.io")


@pytest.mark.asyncio
async def test_disconnect_game_paused(client: AsyncClient, client_two: AsyncClient):
    future = asyncio.get_running_loop().create_future()
    player_service = get_player_service()
    player = await player_service.get(player_id="8cdc1984-e832-48c7-9d89-1d724665bef1")

    sio.enter_room(client_two.get_sid(), room=player.room_id)
    await player_service.update_latest_sid(player=player, latest_sid=client.get_sid())

    @client_two.on("GAME_PAUSED")
    def _(data):
        future.set_result(GamePaused(**data))

    await client.disconnect()
    await asyncio.wait_for(future, timeout=5.0)

    game_paused: GamePaused = future.result()
    assert game_paused.paused_for == 300
    assert game_paused.message == "Player Majiy disconnected, pausing game."
    await client.connect(BASE_URL, socketio_path="/ws/socket.io")


@pytest.mark.asyncio
async def test_get_next_question(client: AsyncClient):
    future = asyncio.get_running_loop().create_future()
    player_service = get_player_service()
    player_id = "8cdc1984-e832-48c7-9d89-1d724665bef1"
    player = await player_service.get(player_id=player_id)
    await player_service.update_latest_sid(latest_sid=client.get_sid(), player=player)

    @client.on("GOT_NEXT_QUESTION")
    def _(data):
        future.set_result(GotNextQuestion(**data))

    room_code = "2257856e-bf37-4cc4-8551-0b1ccdc38c60"
    get_next_question = GetNextQuestion(
        player_id=player_id,
        room_code=room_code,
    )
    sio.enter_room(client.get_sid(), room=room_code)
    await client.emit("GET_NEXT_QUESTION", get_next_question.dict())
    await asyncio.wait_for(future, timeout=5.0)
    got_next_question: GotNextQuestion = future.result()
    assert got_next_question.updated_round.round_changed is True
    assert got_next_question.updated_round.new_round == "opinion"
    assert got_next_question.question.answers is not None  # type: ignore


@pytest.mark.asyncio
async def test_should_not_get_next_question_player_not_in_room(client: AsyncClient):
    future = asyncio.get_running_loop().create_future()
    player_service = get_player_service()
    player_id = "99acb730-93de-4364-917a-8760ee50d0gg"
    player = await player_service.get(player_id=player_id)
    await player_service.update_latest_sid(latest_sid=client.get_sid(), player=player)

    @client.on("ERROR")
    def _(data):
        future.set_result(Error(**data))

    room_code = "2257856e-bf37-4cc4-8551-0b1ccdc38c60"
    get_next_question = GetNextQuestion(
        player_id=player_id,
        room_code=room_code,
    )
    sio.enter_room(client.get_sid(), room=room_code)
    await client.emit("GET_NEXT_QUESTION", get_next_question.dict())
    await asyncio.wait_for(future, timeout=5.0)
    error: Error = future.result()
    assert error.code == "server_error"


@pytest.mark.asyncio
async def test_pause_room(client: AsyncClient):
    future = asyncio.get_running_loop().create_future()

    @client.on("GAME_PAUSED")
    def _(data):
        future.set_result(GamePaused(**data))

    room_code = "2257856e-bf37-4cc4-8551-0b1ccdc38c60"
    pause_game = PauseGame(
        room_code=room_code,
        player_id="8cdc1984-e832-48c7-9d89-1d724665bef1",
    )
    sio.enter_room(client.get_sid(), room=room_code)
    await client.emit("PAUSE_GAME", pause_game.dict())
    await asyncio.wait_for(future, timeout=5.0)

    game_paused: GamePaused = future.result()
    assert game_paused.paused_for == 300
    assert game_paused.message == "Game paused by host."


@pytest.mark.asyncio
async def test_unpause_room(client: AsyncClient):
    future = asyncio.get_running_loop().create_future()
    room_code = "2257856e-bf37-4cc4-8551-0b1ccdc38c60"
    game_state_service = get_game_state_service()
    await game_state_service.pause_game(room_id=room_code)

    @client.on("GAME_UNPAUSED")
    def _(data):
        future.set_result(GameUnpaused())

    unpaused_game = UnpauseGame(
        room_code=room_code,
        player_id="8cdc1984-e832-48c7-9d89-1d724665bef1",
    )
    sio.enter_room(client.get_sid(), room=room_code)
    await client.emit("UNPAUSE_GAME", unpaused_game.dict())
    await asyncio.wait_for(future, timeout=5.0)

    game_paused: GamePaused = future.result()
    assert game_paused


@pytest.mark.asyncio
async def test_disconnect_host(client: AsyncClient, client_two: AsyncClient):
    future = asyncio.get_running_loop().create_future()
    player_service = get_player_service()
    player = await player_service.get(player_id="52dcb730-93ad-4364-917a-8760ee50d0f5")
    sio.enter_room(client_two.get_sid(), room=player.room_id)
    await player_service.update_latest_sid(player=player, latest_sid=client.get_sid())

    @client_two.on("HOST_DISCONNECTED")
    def _(data):
        future.set_result(HostDisconnected(**data))

    await client.disconnect()
    await asyncio.wait_for(future, timeout=5.0)

    new_host_nickname = "CanIHaseeburger"
    host_disconnected: HostDisconnected = future.result()
    assert host_disconnected.new_host_nickname == new_host_nickname
    sio.leave_room(client_two.get_sid(), room=player.room_id)
    await client.connect(BASE_URL, socketio_path="/ws/socket.io")


@pytest.mark.asyncio
async def test_submit_answer(client: AsyncClient):
    future = asyncio.get_running_loop().create_future()
    game_state_service = get_game_state_service()
    room_code = "2257856e-bf37-4cc4-8551-0b1ccdc38c60"
    game_state = await game_state_service.get_game_state_by_room_id(room_id=room_code)
    game_state.action_completed_by = datetime.now() + timedelta(minutes=5)
    game_state.action = FibbingActions.submit_answers
    game_state.state.questions.question_nb = 0  # type: ignore
    await game_state_service.update_state(game_state=game_state, state=game_state.state)  # type: ignore

    @client.on("ANSWER_SUBMITTED_FIBBING_IT")
    def _(data):
        future.set_result(AnswerSubmittedFibbingIt(**data))

    submit_answer = SubmitAnswerFibbingIt(
        room_code=room_code,
        player_id="8cdc1984-e832-48c7-9d89-1d724665bef1",
        answer="lame",
    )
    sio.enter_room(client.get_sid(), room=room_code)
    await client.emit("SUBMIT_ANSWER_FIBBING_IT", submit_answer.dict())
    await asyncio.wait_for(future, timeout=5.0)
    answer_submitted: AnswerSubmittedFibbingIt = future.result()
    assert answer_submitted.all_players_submitted is False


@pytest.mark.asyncio
async def test_submit_answer_out_of_time(client: AsyncClient):
    future = asyncio.get_running_loop().create_future()
    game_state_service = get_game_state_service()
    room_code = "2257856e-bf37-4cc4-8551-0b1ccdc38c60"
    game_state = await game_state_service.get_game_state_by_room_id(room_id=room_code)
    game_state.action = FibbingActions.submit_answers
    game_state.action_completed_by = datetime.now()
    game_state.state.questions.question_nb = 0  # type: ignore
    await game_state_service.update_state(game_state=game_state, state=game_state.state)  # type: ignore

    @client.on("ERROR")
    def _(data):
        future.set_result(Error(**data))

    submit_answer = SubmitAnswerFibbingIt(
        room_code=room_code,
        player_id="8cdc1984-e832-48c7-9d89-1d724665bef1",
        answer="lame",
    )
    sio.enter_room(client.get_sid(), room=room_code)
    await client.emit("SUBMIT_ANSWER_FIBBING_IT", submit_answer.dict())
    await asyncio.wait_for(future, timeout=5.0)
    error: Error = future.result()
    assert error.code == "time_run_out"
