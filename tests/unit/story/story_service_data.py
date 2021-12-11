from typing import List

from app.game.game_exceptions import GameNotFound

add_story_data = [
    (
        {
            "game_name": "quibly",
            "question": "how many fish are there?",
            "round": "pair",
            "answers": [
                {
                    "nickname": "funnyMan420",
                    "answer": "one",
                    "votes": 12341,
                },
                {
                    "nickname": "lima_Bean",
                    "answer": "many",
                    "votes": 0,
                },
            ],
        }
    ),
    (
        {
            "game_name": "drawlosseum",
            "question": "fish",
            "nickname": "i_cannotDraw",
            "round": "drawing",
            "answers": [
                {
                    "start": {
                        "x": 100,
                        "y": -100,
                    },
                    "end": {
                        "x": 90,
                        "y": -100,
                    },
                    "color": "#000000",
                },
            ],
        }
    ),
    (
        {
            "game_name": "fibbing_it",
            "question": "What do you think about horses?",
            "round": "opinion",
            "answers": [
                {
                    "answer": "tasty",
                    "nickname": "!sus",
                },
                {
                    "answer": "lame",
                    "nickname": "!normal_guy",
                },
                {
                    "answer": "lame",
                    "nickname": "normal_guy1",
                },
            ],
        }
    ),
]

add_story_fail_data = [
    (
        {
            "question": "how many fish are there?",
            "round": "pair",
            "answers": [
                {
                    "nickname": "funnyMan420",
                    "answer": "one",
                    "votes": 12341,
                },
                {
                    "nickname": "lima_Bean",
                    "answer": "many",
                    "votes": 0,
                },
            ],
        },
        ValueError,
    ),
    (
        {
            "game_name": "invalid",
            "question": "how many fish are there?",
            "round": "pair",
            "answers": [
                {
                    "nickname": "funnyMan420",
                    "answer": "one",
                    "votes": 12341,
                },
                {
                    "nickname": "lima_Bean",
                    "answer": "many",
                    "votes": 0,
                },
            ],
        },
        GameNotFound,
    ),
    (
        {
            "question": "how many fish are there?",
            "game_name": "quibly",
            "round": "invalid",
            "answers": [
                {
                    "nickname": "funnyMan420",
                    "answer": "one",
                    "votes": 12341,
                },
                {
                    "nickname": "lima_Bean",
                    "answer": "many",
                    "votes": 0,
                },
            ],
        },
        ValueError,
    ),
    (
        {
            "game_name": "quibly",
            "question": "how many fish are there?",
            "answers": [
                {
                    "nickname": "funnyMan420",
                    "answer": "one",
                    "votes": 12341,
                },
                {
                    "nickname": "lima_Bean",
                    "answer": "many",
                    "votes": 0,
                },
            ],
        },
        ValueError,
    ),
    (
        {
            "round": "pair",
            "answers": [
                {
                    "nickname": "funnyMan420",
                    "answer": "one",
                    "votes": 12341,
                },
                {
                    "nickname": "lima_Bean",
                    "answer": "many",
                    "votes": 0,
                },
            ],
        },
        ValueError,
    ),
    (
        {
            "round": "pair",
            "question": "how many fish are there?",
        },
        ValueError,
    ),
    (
        {
            "game_name": "quibly",
            "question": "how many fish are there?",
            "round": "pair",
            "nickname": "hello",
            "answers": [
                {
                    "nickname": "funnyMan420",
                    "answer": "one",
                    "votes": 12341,
                },
                {
                    "nickname": "lima_Bean",
                    "answer": "many",
                    "votes": 0,
                },
            ],
        },
        ValueError,
    ),
    (
        {
            "game_name": "drawlosseum",
            "question": "fish",
            "answers": [
                {
                    "start": {
                        "x": 100,
                        "y": -100,
                    },
                    "end": {
                        "x": 90,
                        "y": -100,
                    },
                    "color": "#000000",
                },
            ],
        },
        ValueError,
    ),
    (
        {
            "nickname": "i_cannotDraw",
            "round": "opinion",
            "answers": [
                {
                    "answer": "tasty",
                    "nickname": "!sus",
                },
                {
                    "answer": "lame",
                    "nickname": "!normal_guy",
                },
                {
                    "answer": "lame",
                    "nickname": "normal_guy1",
                },
            ],
        },
        ValueError,
    ),
    (
        {
            "game_name": "fibbing_it",
            "nickname": "i_cannotDraw",
            "round": "invalid",
            "answers": [
                {
                    "answer": "tasty",
                    "nickname": "!sus",
                },
                {
                    "answer": "lame",
                    "nickname": "!normal_guy",
                },
                {
                    "answer": "lame",
                    "nickname": "normal_guy1",
                },
            ],
        },
        ValueError,
    ),
    (
        {
            "game_name": "fibbing_it",
            "question": "What do you think about horses?",
            "round": "opinion",
            "nickname": "!sus",
            "answers": [
                {
                    "answer": "tasty",
                    "nickname": "!sus",
                },
                {
                    "answer": "lame",
                    "nickname": "!normal_guy",
                },
                {
                    "answer": "lame",
                    "nickname": "normal_guy1",
                },
            ],
        },
        ValueError,
    ),
    (
        {
            "game_name": "fibbing_it",
            "question": "What do you think about horses?",
            "answers": [
                {
                    "answer": "tasty",
                    "nickname": "!sus",
                },
                {
                    "answer": "lame",
                    "nickname": "!normal_guy",
                },
                {
                    "answer": "lame",
                    "nickname": "normal_guy1",
                },
            ],
        },
        ValueError,
    ),
]

all_games_enabled: List[dict] = [
    {
        "name": "quibly",
        "rules_url": "https://gitlab.com/banter-bus/banter-bus-server/-/wikis/docs/rules/quibly",
        "enabled": True,
        "description": "A game about quibbing.",
        "display_name": "Quibly",
    },
    {
        "name": "fibbing_it",
        "rules_url": "https://gitlab.com/banter-bus/banter-bus-server/-/wikis/docs/rules/fibbing_it",
        "enabled": True,
        "description": "A game about lying.",
        "display_name": "Fibbing IT!",
    },
    {
        "name": "drawlosseum",
        "rules_url": "https://google.com/drawlosseum",
        "enabled": True,
        "description": "A game about drawing.",
        "display_name": "Drawlosseum",
    },
]
