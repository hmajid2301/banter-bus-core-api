from app.game.game_exceptions import GameNotFound
from app.question.question_exceptions import (
    InvalidLanguageCode,
    QuestionExistsException,
    QuestionNotFound,
)

add_question_translation_data = [
    (
        "quibly",
        "4b4dd325-04fd-4aa4-9382-2874dcfd5cae",
        "en",
        "english question",
        {
            "question_id": "4b4dd325-04fd-4aa4-9382-2874dcfd5cae",
            "game_name": "quibly",
            "round": "group",
            "enabled": True,
            "content": {"fr": "this is a another question?", "en": "english question"},
        },
    ),
    (
        "fibbing_it",
        "3e2889f6-56aa-4422-a7c5-033eafa9fd39",
        "ur",
        "hello",
        {
            "question_id": "3e2889f6-56aa-4422-a7c5-033eafa9fd39",
            "game_name": "fibbing_it",
            "round": "opinion",
            "group": {"type": "question", "name": "horse_group"},
            "enabled": True,
            "content": {"en": "What do you think about horses?", "ur": "hello"},
        },
    ),
    (
        "drawlosseum",
        "101464a5-337f-4ce7-a4df-2b00764e5d8d",
        "de",
        "german question",
        {
            "question_id": "101464a5-337f-4ce7-a4df-2b00764e5d8d",
            "game_name": "drawlosseum",
            "round": "drawing",
            "enabled": True,
            "content": {"en": "spoon", "de": "german question"},
        },
    ),
]

add_question_translation_fail_data = [
    ("quibly_v3", "815464a5-337f-4ce7-a4df-2b00764e5c6c", "en", "hello", GameNotFound),
    ("quibly", "81546-337f-4ce7-a4df-2b00764e5c6c", "en", "hello", QuestionNotFound),
    ("quibly", "bf64d60c-62ee-420a-976e-bfcaec77ad8b", "en", "hello", QuestionExistsException),
    ("quibly", "815464a5-337f-4ce7-a4df-2b00764e5c6c", "ena", "hello", InvalidLanguageCode),
]


get_question_translation_data = [
    (
        "quibly",
        "4b4dd325-04fd-4aa4-9382-2874dcfd5cae",
        "fr",
        {
            "question_id": "4b4dd325-04fd-4aa4-9382-2874dcfd5cae",
            "game_name": "quibly",
            "round": "group",
            "language_code": "fr",
            "enabled": True,
            "content": "this is a another question?",
        },
    ),
    (
        "quibly",
        "a9c00e19-d41e-4b15-a8bd-ec921af9123d",
        "en",
        {
            "question_id": "a9c00e19-d41e-4b15-a8bd-ec921af9123d",
            "game_name": "quibly",
            "language_code": "en",
            "round": "pair",
            "enabled": False,
            "content": "this is also question?",
        },
    ),
    (
        "fibbing_it",
        "7799e38a-758d-4a1b-a191-99c59440af76",
        "en",
        {
            "question_id": "7799e38a-758d-4a1b-a191-99c59440af76",
            "game_name": "fibbing_it",
            "round": "opinion",
            "language_code": "en",
            "group": {"type": "question", "name": "horse_group"},
            "enabled": True,
            "content": "What do you think about camels?",
        },
    ),
    (
        "fibbing_it",
        "580aeb14-d907-4a22-82c8-f2ac544a2cd1",
        "en",
        {
            "question_id": "580aeb14-d907-4a22-82c8-f2ac544a2cd1",
            "game_name": "fibbing_it",
            "round": "free_form",
            "language_code": "en",
            "group": {"name": "bike_group"},
            "enabled": True,
            "content": "Favourite bike colour?",
        },
    ),
    (
        "fibbing_it",
        "714464a5-337f-4ce7-a4df-2b00764e5c5b",
        "en",
        {
            "question_id": "714464a5-337f-4ce7-a4df-2b00764e5c5b",
            "game_name": "fibbing_it",
            "round": "likely",
            "language_code": "en",
            "enabled": False,
            "content": "to get arrested",
        },
    ),
    (
        "drawlosseum",
        "815464a5-337f-4ce7-a4df-2b00764e5c6c",
        "en",
        {
            "question_id": "815464a5-337f-4ce7-a4df-2b00764e5c6c",
            "game_name": "drawlosseum",
            "round": "drawing",
            "language_code": "en",
            "enabled": True,
            "content": "horse",
        },
    ),
]

get_question_translation_fail_data = [
    ("quibly_v3", "815464a5-337f-4ce7-a4df-2b00764e5c6c", "en", GameNotFound),
    ("quibly", "81546-337f-4ce7-a4df-2b00764e5c6c", "en", QuestionNotFound),
    ("quibly", "815464a5-337f-4ce7-a4df-2b00764e5c6c", "ena", InvalidLanguageCode),
]


remove_question_translation_data = [
    (
        "quibly",
        "4b4dd325-04fd-4aa4-9382-2874dcfd5cae",
        "fr",
        {
            "question_id": "4b4dd325-04fd-4aa4-9382-2874dcfd5cae",
            "game_name": "quibly",
            "round": "group",
            "enabled": True,
            "content": {},
        },
    ),
    (
        "quibly",
        "a9c00e19-d41e-4b15-a8bd-ec921af9123d",
        "en",
        {
            "question_id": "a9c00e19-d41e-4b15-a8bd-ec921af9123d",
            "game_name": "quibly",
            "round": "pair",
            "enabled": False,
            "content": {"ur": "this is also question?", "de": "this is also question?"},
        },
    ),
    (
        "fibbing_it",
        "7799e38a-758d-4a1b-a191-99c59440af76",
        "en",
        {
            "question_id": "7799e38a-758d-4a1b-a191-99c59440af76",
            "game_name": "fibbing_it",
            "round": "opinion",
            "group": {"type": "question", "name": "horse_group"},
            "enabled": True,
            "content": {},
        },
    ),
    (
        "fibbing_it",
        "580aeb14-d907-4a22-82c8-f2ac544a2cd1",
        "en",
        {
            "question_id": "580aeb14-d907-4a22-82c8-f2ac544a2cd1",
            "game_name": "fibbing_it",
            "round": "free_form",
            "group": {"name": "bike_group"},
            "enabled": True,
            "content": {},
        },
    ),
    (
        "fibbing_it",
        "714464a5-337f-4ce7-a4df-2b00764e5c5b",
        "en",
        {
            "question_id": "714464a5-337f-4ce7-a4df-2b00764e5c5b",
            "game_name": "fibbing_it",
            "round": "likely",
            "enabled": False,
            "content": {},
        },
    ),
    (
        "drawlosseum",
        "815464a5-337f-4ce7-a4df-2b00764e5c6c",
        "en",
        {
            "question_id": "815464a5-337f-4ce7-a4df-2b00764e5c6c",
            "game_name": "drawlosseum",
            "round": "drawing",
            "enabled": True,
            "content": {},
        },
    ),
]

remove_question_translation_fail_data = [
    ("quibly_v3", "815464a5-337f-4ce7-a4df-2b00764e5c6c", "en", GameNotFound),
    ("quibly", "81546-337f-4ce7-a4df-2b00764e5c6c", "en", QuestionNotFound),
    ("quibly", "815464a5-337f-4ce7-a4df-2b00764e5c6c", "ena", InvalidLanguageCode),
]
