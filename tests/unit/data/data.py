from app.game_state.game_state_models import (
    FibbingItQuestion,
    FibbingItQuestionsState,
    FibbingItRounds,
    FibbingItState,
)

starting_state = FibbingItState(
    current_faker_sid="a_random_id",
    current_round="opinion",
    questions_to_show=FibbingItQuestionsState(
        current_answers=[],
        rounds=FibbingItRounds(
            opinion=[
                FibbingItQuestion(
                    faker_question="What do you think about camels?",
                    question="What do you think about horses?",
                    answers=["lame", "tasty", "cool"],
                ),
                FibbingItQuestion(
                    faker_question="Cats are cuter than dogs?",
                    question="Dogs are cute?",
                    answers=["Agree", "Strongly Agree", "Disagree"],
                ),
                FibbingItQuestion(
                    faker_question="What is your favourite colour?",
                    question="What is your least favourite colour?",
                    answers=["red", "blue"],
                ),
            ],
            likely=[
                FibbingItQuestion(faker_question="", question="Most likely to get arrested", answers=None),
                FibbingItQuestion(faker_question="", question="Most likely to eat a tub of ice-cream", answers=None),
                FibbingItQuestion(faker_question="", question="Most likely to fight a horse and lose", answers=None),
            ],
            free_form=[
                FibbingItQuestion(faker_question="Favourite bike colour?", question="A funny question?", answers=None),
                FibbingItQuestion(
                    faker_question="what don't you like about cats?",
                    question="what do you like about cats?",
                    answers=None,
                ),
                FibbingItQuestion(faker_question="Least favourite fruit", question="Favourite fruit", answers=None),
            ],
        ),
        question_nb=0,
    ),
)

fibbing_it_update_question_data = [
    (
        {"questions_to_show": {"question_nb": 0}, "current_round": "opinion"},
        {"questions_to_show": {"question_nb": 1}, "current_round": "opinion"},
    ),
    (
        {"questions_to_show": {"question_nb": 2}, "current_round": "opinion"},
        {"questions_to_show": {"question_nb": 0}, "current_round": "likely"},
    ),
    (
        {"questions_to_show": {"question_nb": 1}, "current_round": "likely"},
        {"questions_to_show": {"question_nb": 2}, "current_round": "likely"},
    ),
    (
        {"questions_to_show": {"question_nb": 2}, "current_round": "likely"},
        {"questions_to_show": {"question_nb": 0}, "current_round": "free_form"},
    ),
    (
        {"questions_to_show": {"question_nb": 2}, "current_round": "free_form"},
        None,
    ),
]


fibbing_it_get_next_question_data = [
    (
        {
            "questions_to_show": {"question_nb": 0},
            "current_round": "opinion",
        },
        FibbingItQuestion(
            faker_question="What do you think about camels?",
            question="What do you think about horses?",
            answers=["lame", "tasty", "cool"],
        ),
    ),
    (
        {"questions_to_show": {"question_nb": 1}, "current_round": "likley"},
        FibbingItQuestion(
            faker_question="what don't you like about cats?", question="what do you like about cats?", answers=None
        ),
    ),
    (
        {"questions_to_show": {"question_nb": 1}, "current_round": "free_form"},
        FibbingItQuestion(
            faker_question="what don't you like about cats?", question="what do you like about cats?", answers=None
        ),
    ),
    (
        {"questions_to_show": {"question_nb": 2}, "current_round": "free_form"},
        None,
    ),
]
