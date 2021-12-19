from pydantic import BaseModel

CREATE_ROOM = "CREATE_ROOM"
ROOM_CREATED = "ROOM_CREATED"


class CreateRoom(BaseModel):
    game_name: str


class RoomCreated(BaseModel):
    room_code: str


class Error(BaseModel):
    code: str
    message: str
