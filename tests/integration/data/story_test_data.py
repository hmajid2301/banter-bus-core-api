from fastapi import status

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
        },
        status.HTTP_201_CREATED,
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
        },
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
        },
        status.HTTP_201_CREATED,
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
        },
    ),
    (
        {
            "game_name": "quibly_v2",
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
        status.HTTP_404_NOT_FOUND,
        {},
    ),
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
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        {},
    ),
    (
        {
            "game_name": "quibly",
            "question": "how many fish are there?",
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
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        {},
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
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        {},
    ),
    (
        {
            "game_name": "quibly",
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
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        {},
    ),
    (
        {
            "game_name": "quibly",
            "round": "pair",
            "question": "how many fish are there?",
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        {},
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
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        {},
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
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        {},
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
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        {},
    ),
    (
        {
            "game_name": "fibbing_it",
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
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        {},
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
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        {},
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
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        {},
    ),
]

get_story_data = [
    (
        "1def4233-f674-4a3f-863d-6e850bfbfdb4",
        status.HTTP_200_OK,
        {
            "story_id": "1def4233-f674-4a3f-863d-6e850bfbfdb4",
            "game_name": "quibly",
            "question": "how many fish are there?",
            "round": "pair",
            "answers": [
                {"nickname": "funnyMan420", "answer": "one", "votes": 12341},
                {"nickname": "123456", "answer": "many", "votes": 0},
            ],
        },
    ),
    (
        "a4ffd1c8-93c5-4f4c-8ace-71996edcbcb7",
        status.HTTP_200_OK,
        {
            "story_id": "a4ffd1c8-93c5-4f4c-8ace-71996edcbcb7",
            "game_name": "drawlosseum",
            "question": "fish",
            "nickname": "i_cannotDraw",
            "answers": [{"start": {"x": 100, "y": -100}, "end": {"x": 90, "y": -100}, "color": "#000"}],
        },
    ),
    (
        "50-011c-45d8-98f7-819520c253b6",
        status.HTTP_404_NOT_FOUND,
        {},
    ),
]

delete_story_data = [
    (
        "1def4233-f674-4a3f-863d-6e850bfbfdb4",
        status.HTTP_200_OK,
    ),
    (
        "a4ffd1c8-93c5-4f4c-8ace-71996edcbcb7",
        status.HTTP_200_OK,
    ),
    (
        "50-011c-45d8-98f7-819520c253b6",
        status.HTTP_404_NOT_FOUND,
    ),
]
