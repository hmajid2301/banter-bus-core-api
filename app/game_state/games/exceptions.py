from app.core.exceptions import NotFoundException


class InvalidGameRound(Exception):
    pass


class GameNotFound(NotFoundException):
    pass
