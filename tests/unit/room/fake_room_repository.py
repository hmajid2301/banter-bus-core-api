from datetime import datetime

from app.player.player_exceptions import PlayerNotFound
from app.player.player_models import Player
from app.room.room_exceptions import RoomExistsException, RoomNotFound
from app.room.room_models import Room, RoomState
from app.room.room_repository import RoomRepository


class FakeRoomRepository(RoomRepository):
    def __init__(self, rooms: list[Room]):
        self.rooms = rooms

    async def add(self, new_room: Room):
        for room in self.rooms:
            if room.room_id == new_room.room_id:
                raise RoomExistsException("room already exists")

        self.rooms.append(new_room)

    async def add_player(self, room: Room, player: Player):
        room.players.append(player)

    async def get(self, id_: str) -> Room:
        for room in self.rooms:
            if room.room_id == id_:
                return room
        raise RoomNotFound("room not found", id_=id_)

    async def get_room_by_player_id(self, player_id: str) -> Room:
        for room in self.rooms:
            for player in room.players:
                if player.player_id == player_id:
                    return room
        raise RoomNotFound("room not found using player id", id_=player_id)

    async def get_player(self, player_id: str) -> Player:
        for room in self.rooms:
            for player in room.players:
                if player.player_id == player_id:
                    return player
        raise PlayerNotFound("player not found")

    async def get_all_players(self, room_id: str) -> list[Player]:
        room = await self.get(id_=room_id)
        return room.players

    async def get_player_by_sid(self, sid: str) -> Player:
        for room in self.rooms:
            for player in room.players:
                if player.latest_sid == sid:
                    return player
        raise PlayerNotFound("player not found")

    async def get_player_by_nickname(self, room_id: str, nickname: str) -> Player:
        for room in self.rooms:
            for player in room.players:
                if player.nickname == nickname and room.room_id == room_id:
                    return player
        raise PlayerNotFound("player not found")

    async def remove(self, id_: str):
        return await super().remove(id_)

    async def remove_player(self, room: Room, nickname: str) -> Player:
        player = await self.get_player_by_nickname(room_id=room.room_id, nickname=nickname)
        room.players = [player for player in room.players if player.nickname != nickname]
        return player

    async def update_host(self, room: Room, player_id: str):
        for r in self.rooms:
            if r.room_id == room.room_id:
                r.host = player_id

    async def update_game_state(self, room: Room, new_room_state: RoomState):
        for r in self.rooms:
            if r.room_id == room.room_id:
                r.state = new_room_state

    async def update_player_disconnected_at(self, sid: str, disconnected_at: datetime | None = None):
        player = await self.get_player_by_sid(sid)
        player.disconnected_at = disconnected_at

    async def update_sid(self, player_id: str, sid: str):
        player = await self.get_player(player_id=player_id)
        player.latest_sid = sid
