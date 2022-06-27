from app.game_state.game_state_models import (
    FibbingItQuestion,
    FibbingItQuestionsState,
    FibbingItRounds,
    FibbingItState,
)

starting_state = FibbingItState(
    current_fibber_id="a_random_id",
    current_round="opinion",
    questions=FibbingItQuestionsState(
        current_answers={},
        rounds=FibbingItRounds(
            opinion=[
                FibbingItQuestion(
                    fibber_question="What do you think about camels?",
                    question="What do you think about horses?",
                    answers=["lame", "tasty", "cool"],
                ),
                FibbingItQuestion(
                    fibber_question="Cats are cuter than dogs?",
                    question="Dogs are cute?",
                    answers=["Agree", "Strongly Agree", "Disagree"],
                ),
                FibbingItQuestion(
                    fibber_question="What is your favourite colour?",
                    question="What is your least favourite colour?",
                    answers=["red", "blue"],
                ),
            ],
            likely=[
                FibbingItQuestion(fibber_question="", question="Most likely to get arrested", answers=None),
                FibbingItQuestion(fibber_question="", question="Most likely to eat a tub of ice-cream", answers=None),
                FibbingItQuestion(fibber_question="", question="Most likely to fight a horse and lose", answers=None),
            ],
            free_form=[
                FibbingItQuestion(fibber_question="Favourite bike colour?", question="A funny question?", answers=None),
                FibbingItQuestion(
                    fibber_question="what don't you like about cats?",
                    question="what do you like about cats?",
                    answers=None,
                ),
                FibbingItQuestion(fibber_question="Least favourite fruit", question="Favourite fruit", answers=None),
            ],
        ),
        question_nb=0,
    ),
)

fibbing_it_update_question_data = [
    (
        {"questions": {"question_nb": 0}, "current_round": "opinion"},
        {"questions": {"question_nb": 1}, "current_round": "opinion"},
    ),
    (
        {"questions": {"question_nb": 2}, "current_round": "opinion"},
        {"questions": {"question_nb": 0}, "current_round": "likely"},
    ),
    (
        {"questions": {"question_nb": 1}, "current_round": "likely"},
        {"questions": {"question_nb": 2}, "current_round": "likely"},
    ),
    (
        {"questions": {"question_nb": 2}, "current_round": "likely"},
        {"questions": {"question_nb": 0}, "current_round": "free_form"},
    ),
    (
        {"questions": {"question_nb": 2}, "current_round": "free_form"},
        None,
    ),
]


fibbing_it_get_next_question_data = [
    (
        {
            "questions": {"question_nb": 0},
            "current_round": "opinion",
        },
        FibbingItQuestion(
            fibber_question="What do you think about camels?",
            question="What do you think about horses?",
            answers=["lame", "tasty", "cool"],
        ),
    ),
    (
        {"questions": {"question_nb": 1}, "current_round": "likley"},
        FibbingItQuestion(
            fibber_question="what don't you like about cats?", question="what do you like about cats?", answers=None
        ),
    ),
    (
        {"questions": {"question_nb": 1}, "current_round": "free_form"},
        FibbingItQuestion(
            fibber_question="what don't you like about cats?", question="what do you like about cats?", answers=None
        ),
    ),
    (
        {"questions": {"question_nb": 2}, "current_round": "free_form"},
        None,
    ),
]
