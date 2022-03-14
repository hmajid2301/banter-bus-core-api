from app.event_models import EventModel

CREATE_ROOM = "CREATE_ROOM"
ROOM_CREATED = "ROOM_CREATED"
PERMANENTLY_DISCONNECT_PLAYER = "PERMANENTLY_DISCONNECT_PLAYER"
PERMANENTLY_DISCONNECTED_PLAYER = "PERMANENTLY_DISCONNECTED_PLAYER"


class CreateRoom(EventModel):
    @property
    def event_name(self):
        return CREATE_ROOM


class RoomCreated(EventModel):
    room_code: str

    @property
    def event_name(self):
        return ROOM_CREATED


class PermanentlyDisconnectPlayer(EventModel):
    nickname: str
    room_code: str

    @property
    def event_name(self):
        return PERMANENTLY_DISCONNECT_PLAYER


class PermanentlyDisconnectedPlayer(EventModel):
    nickname: str

    @property
    def event_name(self):
        return PERMANENTLY_DISCONNECTED_PLAYER
