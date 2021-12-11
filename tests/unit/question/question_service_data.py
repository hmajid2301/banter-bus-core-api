from app.game.game_exceptions import GameNotFound
from app.question.question_exceptions import (
    InvalidLanguageCode,
    InvalidLimit,
    QuestionExistsException,
)

add_question_data = [
    (
        {"content": "this is a question?", "round": "pair", "game_name": "quibly"},
        {
            "question_id": "5ecd5827-b6ef-4067-b5ac-3ceac07dde9f",
            "game_name": "quibly",
            "round": "pair",
            "enabled": True,
            "content": {"en": "this is a question?"},
        },
    ),
    (
        {
            "content": "what is the funniest thing ever told?",
            "round": "answer",
            "language_code": "de",
            "game_name": "quibly",
        },
        {
            "question_id": "5ecd5827-b6ef-4067-b5ac-3ceac07dde9f",
            "game_name": "quibly",
            "round": "answer",
            "enabled": True,
            "content": {"de": "what is the funniest thing ever told?"},
        },
    ),
    (
        {"content": "what does ATGM stand for?", "round": "group", "game_name": "quibly"},
        {
            "question_id": "5ecd5827-b6ef-4067-b5ac-3ceac07dde9f",
            "game_name": "quibly",
            "round": "group",
            "enabled": True,
            "content": {"en": "what does ATGM stand for?"},
        },
    ),
    (
        {"content": "pencil", "game_name": "drawlosseum", "round": "drawing"},
        {
            "question_id": "5ecd5827-b6ef-4067-b5ac-3ceac07dde9f",
            "game_name": "drawlosseum",
            "round": "drawing",
            "enabled": True,
            "content": {"en": "pencil"},
        },
    ),
    (
        {
            "content": "do you love bikes?",
            "language_code": "en",
            "round": "opinion",
            "game_name": "fibbing_it",
            "group": {
                "name": "bike",
                "type": "question",
            },
        },
        {
            "question_id": "5ecd5827-b6ef-4067-b5ac-3ceac07dde9f",
            "game_name": "fibbing_it",
            "enabled": True,
            "round": "opinion",
            "content": {"en": "do you love bikes?"},
            "group": {
                "name": "bike",
                "type": "question",
            },
        },
    ),
    (
        {
            "content": "bikes are super cool",
            "round": "opinion",
            "game_name": "fibbing_it",
            "group": {
                "name": "bike",
                "type": "answer",
            },
        },
        {
            "question_id": "5ecd5827-b6ef-4067-b5ac-3ceac07dde9f",
            "game_name": "fibbing_it",
            "enabled": True,
            "round": "opinion",
            "content": {"en": "bikes are super cool"},
            "group": {
                "name": "bike",
                "type": "answer",
            },
        },
    ),
    (
        {
            "game_name": "fibbing_it",
            "content": "what is the fastest horse?",
            "round": "free_form",
            "group": {
                "name": "horse",
            },
        },
        {
            "question_id": "5ecd5827-b6ef-4067-b5ac-3ceac07dde9f",
            "game_name": "fibbing_it",
            "enabled": True,
            "round": "free_form",
            "content": {"en": "what is the fastest horse?"},
            "group": {
                "name": "horse",
            },
        },
    ),
    (
        {
            "game_name": "fibbing_it",
            "content": "to never eat a vegetable again?",
            "round": "likely",
        },
        {
            "question_id": "5ecd5827-b6ef-4067-b5ac-3ceac07dde9f",
            "game_name": "fibbing_it",
            "enabled": True,
            "round": "likely",
            "content": {"en": "to never eat a vegetable again?"},
        },
    ),
]

add_question_data_fail = [
    (
        {
            "game_name": "quibly",
            "content": "hello",
            "round": "invalid",
        },
        ValueError,
    ),
    (
        {
            "game_name": "quibly",
            "content": "hello",
        },
        ValueError,
    ),
    (
        {
            "game_name": "drawlosseum",
        },
        ValueError,
    ),
    (
        {
            "game_name": "fibbing_it",
            "content": "What is the fastest horse?",
            "round": "invalid",
            "group": {"name": "horse"},
        },
        ValueError,
    ),
    (
        {
            "game_name": "fibbing_it",
            "content": "super love",
            "round": "opinion",
            "group": {"name": "horse", "type": "invalid"},
        },
        ValueError,
    ),
    (
        {
            "game_name": "fibbing_it",
            "content": "super love",
            "round": "opinion",
        },
        ValueError,
    ),
    (
        {
            "game_name": "fibbing_it",
            "content": "super love",
            "round": "opinion",
            "group": {"name": "horse", "type": "answer"},
            "language_code": "enda",
        },
        InvalidLanguageCode,
    ),
    (
        {
            "game_name": "fibbing_it_v3",
            "content": "super love",
            "round": "opinion",
            "group": {"name": "horse", "type": "answer"},
        },
        GameNotFound,
    ),
    ({"game_name": "quibly", "round": "pair", "content": "this is a question?"}, QuestionExistsException),
    ({"game_name": "quibly", "round": "answer", "language_code": "de", "content": "german"}, QuestionExistsException),
    (
        {"game_name": "quibly", "round": "group", "language_code": "fr", "content": "this is a another question?"},
        QuestionExistsException,
    ),
    (
        {
            "game_name": "fibbing_it",
            "round": "opinion",
            "language_code": "en",
            "content": "What do you think about horses?",
            "group": {
                "name": "horse_group",
                "type": "question",
            },
        },
        QuestionExistsException,
    ),
    (
        {
            "game_name": "fibbing_it",
            "round": "free_form",
            "content": "A funny question?",
            "group": {
                "name": "bike_group",
            },
        },
        QuestionExistsException,
    ),
    (
        {
            "game_name": "fibbing_it",
            "round": "likely",
            "content": "to eat ice-cream from the tub",
        },
        QuestionExistsException,
    ),
    (
        {
            "game_name": "drawlosseum",
            "content": "spoon",
            "round": "drawing",
        },
        QuestionExistsException,
    ),
]

get_random_questions_data = [
    (
        "quibly",
        "pair",
        "en",
        2,
        "",
        2,
    ),
    (
        "quibly",
        "answer",
        "de",
        1,
        "",
        1,
    ),
    (
        "quibly",
        "group",
        "fr",
        1,
        "",
        1,
    ),
    (
        "quibly",
        "group",
        "fr",
        10,
        "",
        1,
    ),
    (
        "quibly",
        "group",
        "ur",
        10,
        "",
        0,
    ),
    (
        "fibbing_it",
        "opinion",
        "en",
        99,
        "horse_group",
        5,
    ),
    (
        "fibbing_it",
        "free_form",
        "en",
        54,
        "bike_group",
        2,
    ),
    (
        "fibbing_it",
        "likely",
        "en",
        5,
        "",
        2,
    ),
    (
        "drawlosseum",
        "drawing",
        "en",
        5,
        "",
        2,
    ),
]

get_random_questions_data_fail = [
    (
        "quibly_v3",
        "group",
        "fr",
        10,
        "",
        GameNotFound,
    ),
    (
        "quibly",
        "group",
        "fr",
        -1,
        "",
        InvalidLimit,
    ),
]

get_groups_data = [
    ("quibly", "pair", 1),
    ("fibbing_it", "opinion", 1),
    ("fibbing_it", "free_form", 1),
    ("fibbing_it", "likely", 1),
    ("drawlosseum", "drawing", 1),
]

get_groups_data_fail = [
    ("quibly_v3", "pair", 1, GameNotFound),
    ("quibly", "round", 1, ValueError),
    ("quibly", "pair", -1, InvalidLimit),
]

get_question_ids_data = [
    (
        "fibbing_it",
        "",
        5,
        {
            "question_ids": [
                "3e2889f6-56aa-4422-a7c5-033eafa9fd39",
                "7799e38a-758d-4a1b-a191-99c59440af76",
                "03a462ba-f483-4726-aeaf-b8b6b03ce3e2",
                "d5aa9153-f48c-45cc-b411-fb9b2d38e78f",
                "138bc208-2849-41f3-bbd8-3226a96c5370",
            ],
            "cursor": "138bc208-2849-41f3-bbd8-3226a96c5370",
        },
    ),
    (
        "fibbing_it",
        "138bc208-2849-41f3-bbd8-3226a96c5370",
        5,
        {
            "question_ids": [
                "580aeb14-d907-4a22-82c8-f2ac544a2cd1",
                "aa9fe2b5-79b5-458d-814b-45ff95a617fc",
                "d80f2d90-0fb0-462a-8fbd-1aa00b4e42a5",
                "d6318b0d-29e1-4f10-b6a7-37a648364ca6",
                "714464a5-337f-4ce7-a4df-2b00764e5c5b",
            ],
            "cursor": "714464a5-337f-4ce7-a4df-2b00764e5c5b",
        },
    ),
    (
        "drawlosseum",
        "",
        5,
        {
            "question_ids": ["815464a5-337f-4ce7-a4df-2b00764e5c6c", "101464a5-337f-4ce7-a4df-2b00764e5d8d"],
        },
    ),
    (
        "quibly",
        "",
        2,
        {
            "question_ids": ["4d18ac45-8034-4f8e-b636-cf730b17e51a", "a9c00e19-d41e-4b15-a8bd-ec921af9123d"],
            "cursor": "a9c00e19-d41e-4b15-a8bd-ec921af9123d",
        },
    ),
    (
        "quibly",
        "a9c00e19-d41e-4b15-a8bd-ec921af9123d",
        3,
        {
            "question_ids": ["bf64d60c-62ee-420a-976e-bfcaec77ad8b", "4b4dd325-04fd-4aa4-9382-2874dcfd5cae"],
        },
    ),
]

get_question_ids_data_fail = [
    (
        "fibbing_it_v3",
        "",
        5,
        GameNotFound,
    ),
    ("fibbing_it", "", -1, InvalidLimit),
]

get_question_data = [
    (
        "4d18ac45-8034-4f8e-b636-cf730b17e51a",
        "quibly",
        {
            "question_id": "4d18ac45-8034-4f8e-b636-cf730b17e51a",
            "game_name": "quibly",
            "round": "pair",
            "enabled": True,
            "content": {"en": "this is a question?", "ur": "this is a question?", "de": "this is a question?"},
        },
    ),
    (
        "7799e38a-758d-4a1b-a191-99c59440af76",
        "fibbing_it",
        {
            "question_id": "7799e38a-758d-4a1b-a191-99c59440af76",
            "game_name": "fibbing_it",
            "round": "opinion",
            "group": {"type": "question", "name": "horse_group"},
            "enabled": True,
            "content": {"en": "What do you think about camels?"},
        },
    ),
    (
        "101464a5-337f-4ce7-a4df-2b00764e5d8d",
        "drawlosseum",
        {
            "question_id": "101464a5-337f-4ce7-a4df-2b00764e5d8d",
            "game_name": "drawlosseum",
            "round": "drawing",
            "enabled": True,
            "content": {"en": "spoon"},
        },
    ),
]

update_enabled_status_question_data = [
    ("quibly", "a9c00e19-d41e-4b15-a8bd-ec921af9123d"),
    (
        "quibly",
        "4d18ac45-8034-4f8e-b636-cf730b17e51a",
    ),
]
