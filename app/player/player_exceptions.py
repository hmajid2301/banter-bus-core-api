from app.core.exceptions import ExistsException, NotFoundException


class PlayerExistsException(ExistsException):
    pass


class PlayerNotFound(NotFoundException):
    pass


class NicknameExistsException(ExistsException):
    def __init__(self, msg: str, nickname: str) -> None:
        self.msg = msg
        self.nickname = nickname
