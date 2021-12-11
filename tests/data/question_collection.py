from typing import List

from app.question.question_models import Question

questions: List[Question] = [
    Question(
        **{
            "question_id": "4d18ac45-8034-4f8e-b636-cf730b17e51a",
            "game_name": "quibly",
            "round": "pair",
            "enabled": True,
            "content": {"en": "this is a question?", "ur": "this is a question?", "de": "this is a question?"},
        }
    ),
    Question(
        **{
            "question_id": "a9c00e19-d41e-4b15-a8bd-ec921af9123d",
            "game_name": "quibly",
            "round": "pair",
            "enabled": False,
            "content": {"en": "this is also question?", "ur": "this is also question?", "de": "this is also question?"},
        }
    ),
    Question(
        **{
            "question_id": "bf64d60c-62ee-420a-976e-bfcaec77ad8b",
            "game_name": "quibly",
            "round": "answer",
            "enabled": True,
            "content": {"en": "pink mustard", "de": "german"},
        }
    ),
    Question(
        **{
            "question_id": "4b4dd325-04fd-4aa4-9382-2874dcfd5cae",
            "game_name": "quibly",
            "round": "group",
            "enabled": True,
            "content": {"fr": "this is a another question?"},
        }
    ),
    Question(
        **{
            "question_id": "3e2889f6-56aa-4422-a7c5-033eafa9fd39",
            "game_name": "fibbing_it",
            "round": "opinion",
            "group": {"type": "question", "name": "horse_group"},
            "enabled": True,
            "content": {"en": "What do you think about horses?"},
        }
    ),
    Question(
        **{
            "question_id": "7799e38a-758d-4a1b-a191-99c59440af76",
            "game_name": "fibbing_it",
            "round": "opinion",
            "group": {"type": "question", "name": "horse_group"},
            "enabled": True,
            "content": {"en": "What do you think about camels?"},
        }
    ),
    Question(
        **{
            "question_id": "03a462ba-f483-4726-aeaf-b8b6b03ce3e2",
            "game_name": "fibbing_it",
            "round": "opinion",
            "group": {"type": "answer", "name": "horse_group"},
            "enabled": True,
            "content": {"en": "cool"},
        }
    ),
    Question(
        **{
            "question_id": "d5aa9153-f48c-45cc-b411-fb9b2d38e78f",
            "game_name": "fibbing_it",
            "round": "opinion",
            "group": {"type": "answer", "name": "horse_group"},
            "enabled": True,
            "content": {"en": "tasty"},
        }
    ),
    Question(
        **{
            "question_id": "138bc208-2849-41f3-bbd8-3226a96c5370",
            "game_name": "fibbing_it",
            "round": "opinion",
            "group": {"type": "answer", "name": "horse_group"},
            "enabled": True,
            "content": {"en": "lame"},
        }
    ),
    Question(
        **{
            "question_id": "580aeb14-d907-4a22-82c8-f2ac544a2cd1",
            "game_name": "fibbing_it",
            "round": "free_form",
            "group": {"name": "bike_group"},
            "enabled": True,
            "content": {"en": "Favourite bike colour?"},
        }
    ),
    Question(
        **{
            "question_id": "aa9fe2b5-79b5-458d-814b-45ff95a617fc",
            "game_name": "fibbing_it",
            "round": "free_form",
            "group": {"name": "bike_group"},
            "enabled": False,
            "content": {"en": "A funny question?"},
        }
    ),
    Question(
        **{
            "question_id": "d80f2d90-0fb0-462a-8fbd-1aa00b4e42a5",
            "game_name": "fibbing_it",
            "round": "free_form",
            "group": {"name": "cat_group"},
            "enabled": False,
            "content": {"it": "Perché sono superiori i gatti di Liam?"},
        }
    ),
    Question(
        **{
            "question_id": "d6318b0d-29e1-4f10-b6a7-37a648364ca6",
            "game_name": "fibbing_it",
            "round": "likely",
            "enabled": True,
            "content": {"en": "to eat ice-cream from the tub"},
        }
    ),
    Question(
        **{
            "question_id": "714464a5-337f-4ce7-a4df-2b00764e5c5b",
            "game_name": "fibbing_it",
            "round": "likely",
            "enabled": False,
            "content": {"en": "to get arrested"},
        }
    ),
    Question(
        **{
            "question_id": "815464a5-337f-4ce7-a4df-2b00764e5c6c",
            "game_name": "drawlosseum",
            "round": "drawing",
            "enabled": True,
            "content": {"en": "horse"},
        }
    ),
    Question(
        **{
            "question_id": "101464a5-337f-4ce7-a4df-2b00764e5d8d",
            "game_name": "drawlosseum",
            "round": "drawing",
            "enabled": True,
            "content": {"en": "spoon"},
        }
    ),
]
