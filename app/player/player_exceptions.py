from app.core.exceptions import ExistsException


class PlayerExistsException(ExistsException):
    pass


class NicknameExistsException(ExistsException):
    def __init__(self, msg: str, nickname: str) -> None:
        self.msg = msg
        self.nickname = nickname
