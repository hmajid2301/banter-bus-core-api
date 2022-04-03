get_questions_mock_data = {
    "http://localhost/game/fibbing_it/question/group:random?round=opinion&limit=3": {
        "groups": ["horse_group", "animal_group", "colour_group"]
    },
    "http://localhost/game/fibbing_it/question/group:random?round=free_form&limit=3": {
        "groups": ["bike_group", "cat_group", "programmer_group"]
    },
    "http://localhost/game/fibbing_it/question:random?round=opinion&group_name=horse_group": [
        {"question_id": "138bc208-2849-41f3-bbd8-3226a96c5370", "content": "lame", "type": "answer"},
        {
            "question_id": "7799e38a-758d-4a1b-a191-99c59440af76",
            "content": "What do you think about camels?",
            "type": "question",
        },
        {
            "question_id": "3e2889f6-56aa-4422-a7c5-033eafa9fd39",
            "content": "What do you think about horses?",
            "type": "question",
        },
        {"question_id": "d5aa9153-f48c-45cc-b411-fb9b2d38e78f", "content": "tasty", "type": "answer"},
        {"question_id": "03a462ba-f483-4726-aeaf-b8b6b03ce3e2", "content": "cool", "type": "answer"},
    ],
    "http://localhost/game/fibbing_it/question:random?round=opinion&group_name=animal_group": [
        {"question_id": "d5aa9153-f48c-45cc-b411-fb9b2d38e7ee", "content": "Agree", "type": "answer"},
        {"question_id": "138bc208-2849-41f3-bbd8-3226a96c5311", "content": "Strongly Agree", "type": "answer"},
        {"question_id": "03a462ba-f483-4726-aeaf-b8b6b03ce3aa", "content": "Disagree", "type": "answer"},
        {
            "question_id": "7799e38a-758d-4a1b-a191-99c59440afee",
            "content": "Cats are cuter than dogs?",
            "type": "question",
        },
        {
            "question_id": "3e2889f6-56aa-4422-a7c5-033eafa9fd33",
            "content": "Dogs are cute?",
            "type": "question",
        },
    ],
    "http://localhost/game/fibbing_it/question:random?round=opinion&group_name=colour_group": [
        {
            "question_id": "7799e38a-758d-4a1b-a191-99c59440afdd",
            "content": "What is your favourite colour?",
            "type": "question",
        },
        {
            "question_id": "3e2889f6-56aa-4422-a7c5-033eafa9fd22",
            "content": "What is your least favourite colour?",
            "type": "question",
        },
        {"question_id": "03a462ba-f483-4726-aeaf-b8b6b03ce3ff", "content": "red", "type": "answer"},
        {"question_id": "d5aa9153-f48c-45cc-b411-fb9b2d38e78d", "content": "blue", "type": "answer"},
    ],
    "http://localhost/game/fibbing_it/question:random?round=free_form&group_name=cat_group": [
        {
            "question_id": "d80f2d90-0fb0-462a-8fbd-1aa00b4e42cc",
            "content": "what don't you like about cats?",
        },
        {
            "question_id": "d80f2d90-0fb0-462a-8fbd-1aa00b4e42ff",
            "content": "what do you like about cats?",
        },
    ],
    "http://localhost/game/fibbing_it/question:random?round=free_form&group_name=bike_group": [
        {
            "question_id": "aa9fe2b5-79b5-458d-814b-45ff95a617fc",
            "content": "A funny question?",
        },
        {
            "question_id": "580aeb14-d907-4a22-82c8-f2ac544a2cd1",
            "content": "Favourite bike colour?",
        },
    ],
    "http://localhost/game/fibbing_it/question:random?round=free_form&group_name=programmer_group": [
        {
            "question_id": "ee9fe2b5-79b5-458d-814b-45ff95a617fc",
            "content": "Least favourite fruit",
        },
        {
            "question_id": "9900aeb14-d907-4a22-82c8-f2ac544a2cd1",
            "content": "Favourite fruit",
        },
    ],
    "http://localhost/game/fibbing_it/question:random?round=likely&limit=3": [
        {
            "question_id": "580aeb14-d907-4a22-82c8-f2ac544a2cee",
            "content": "Most likely to get arrested",
        },
        {
            "question_id": "890aeb14-d907-4a22-82c8-f2ac544a2cee",
            "content": "Most likely to eat a tub of ice-cream",
        },
        {
            "question_id": "778aeb14-d907-4a22-82c8-f2ac544a2cee",
            "content": "Most likely to fight a horse and lose",
        },
    ],
}
