from datetime import datetime, timedelta
from typing import List

from app.player.player_models import Player

players: List[Player] = [
    Player(
        **{
            "room_id": "5a18ac45-9876-4f8e-b636-cf730b17e59l",
            "player_id": "52dcb730-93ad-4364-917a-8760ee50d0f5",
            "nickname": "Majiy",
            "avatar": b"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg",
            "latest_sid": "123456",
        },
    ),
    Player(
        **{
            "room_id": "5a18ac45-9876-4f8e-b636-cf730b17e59l",
            "player_id": "66dcb730-93de-4364-917a-8760ee50d0ff",
            "nickname": "CanIHaseeburger",
            "avatar": b"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg",
            "latest_sid": "654321",
        },
    ),
    Player(
        **{
            "room_id": "5a18ac45-9876-4f8e-b636-cf730b17e59l",
            "player_id": "778cb730-93de-4364-917a-8760ee50d0ff",
            "nickname": "AnotherPlayer",
            "avatar": b"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg",
            "latest_sid": "ABCDEFG",
            "disconnected_at": datetime.now() - timedelta(minutes=10),
        },
    ),
    Player(
        **{
            "room_id": "5a18ac45-9876-4f8e-b636-cf730b17e59l",
            "player_id": "8760ee50d0ff-93de-4364-917a-778cb730",
            "nickname": "PlayerV2",
            "avatar": b"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg",
            "latest_sid": "HHHJJJKKKK",
            "disconnected_at": datetime.now() - timedelta(minutes=6),
        },
    ),
    Player(
        **{
            "room_id": "5a18ac45-9876-4f8e-b636-cf730b17e59l",
            "player_id": "99acb730-93de-4364-917a-8760ee50d0gg",
            "nickname": "DisconnectedPlayer",
            "avatar": b"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg",
            "latest_sid": "GfAVCD",
            "disconnected_at": datetime.now() - timedelta(minutes=3),
        },
    ),
    Player(
        **{
            "room_id": "a4ffd1c8-93c5-4f4c-8ace-71996edcbcb7",
            "player_id": "aacd1fa2-404b-4dfc-ac06-7355e99b5117",
            "nickname": "xoxoProSniperzxoxo",
            "avatar": b"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg",
            "latest_sid": "654321",
        },
    ),
    Player(
        **{
            "room_id": "a4ffd1c8-93c5-4f4c-8ace-71996edcbcb7",
            "player_id": "509fe727-a4f6-4d91-ac46-c1e2d5ff6810",
            "nickname": "Majiy",
            "avatar": b"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg",
            "latest_sid": "123456",
        },
    ),
    Player(
        **{
            "room_id": "2257856e-bf37-4cc4-8551-0b1ccdc38c60",
            "player_id": "8cdc1984-e832-48c7-9d89-1d724665bef1",
            "nickname": "Majiy",
            "avatar": b"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg",
            "latest_sid": "123456",
        },
    ),
    Player(
        **{
            "room_id": "2257856e-bf37-4cc4-8551-0b1ccdc38c60",
            "player_id": "02b38b51-3926-4b11-829a-54aa848f992f",
            "nickname": "AnotherPlayer",
            "avatar": b"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg",
            "latest_sid": "65371",
        },
    ),
    Player(
        **{
            "room_id": "2257856e-bf37-4cc4-8551-0b1ccdc38c60",
            "player_id": "49e810c5-c0ae-4443-88da-9fa4788541f2",
            "nickname": "Lima",
            "avatar": b"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg",
            "latest_sid": "abcd1234",
        },
    ),
    Player(
        **{
            "room_id": "2257856e-bf37-4cc4-8551-0b1ccdc38c60",
            "player_id": "63fd683c-570a-49ac-b2bb-b1f306296ea7",
            "nickname": "YAP",
            "avatar": b"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg",
            "latest_sid": "zxcvb980",
        },
    ),
]
