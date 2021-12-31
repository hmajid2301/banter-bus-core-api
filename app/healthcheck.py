from app.room.room_models import Room


def db_healthcheck() -> bool:
    try:
        Room.find()
        return False
    except Exception:
        return False
