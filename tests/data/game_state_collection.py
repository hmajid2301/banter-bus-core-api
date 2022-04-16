from typing import List

from app.game_state.game_state_models import (
    FibbingItQuestion,
    FibbingItQuestionsState,
    FibbingItRounds,
    FibbingItState,
    GameState,
    PlayerScore,
)

game_states: List[GameState] = [
    GameState(
        room_id="2257856e-bf37-4cc4-8551-0b1ccdc38c60",
        game_name="fibbing_it",
        player_scores=[
            PlayerScore(player_id="5fcfe479-1984-471d-bd23-136e85696da4", score=0),
            PlayerScore(player_id="f921d6cf-b59f-4a3c-9e58-f0273121cc1a", score=0),
            PlayerScore(player_id="285243e1-0656-44cc-9549-fea3a17e2540", score=0),
        ],
        state=FibbingItState(
            current_faker_sid="285243e1-0656-44cc-9549-fea3a17e2540",
            questions_to_show=FibbingItQuestionsState(
                rounds=FibbingItRounds(
                    opinion=[
                        FibbingItQuestion(
                            faker_question="What do you think about horses?",
                            question="What do you think about camels?",
                            answers=["lame", "tasty", "cool"],
                        ),
                        FibbingItQuestion(
                            faker_question="Dogs are cute?",
                            question="Cats are cuter than dogs?",
                            answers=["Agree", "Strongly Agree", "Disagree"],
                        ),
                        FibbingItQuestion(
                            faker_question="What is your least favourite colour?",
                            question="What is your favourite colour?",
                            answers=["red", "blue"],
                        ),
                    ],
                    likely=[
                        FibbingItQuestion(
                            faker_question="",
                            question="Most likely to get arrested",
                            answers=["Richard", "Michael", "Brandon"],
                        ),
                        FibbingItQuestion(
                            faker_question="",
                            question="Most likely to eat a tub of ice-cream",
                            answers=["Richard", "Michael", "Brandon"],
                        ),
                        FibbingItQuestion(
                            faker_question="",
                            question="Most likely to fight a horse and lose",
                            answers=["Richard", "Michael", "Brandon"],
                        ),
                    ],
                    free_form=[
                        FibbingItQuestion(
                            faker_question="A funny question?", question="Favourite bike colour?", answers=None
                        ),
                        FibbingItQuestion(
                            faker_question="what do you like about cats?",
                            question="what don't you like about cats?",
                            answers=None,
                        ),
                        FibbingItQuestion(
                            faker_question="Favourite fruit", question="Least favourite fruit", answers=None
                        ),
                    ],
                ),
                question_nb=-1,
                current_answers=[],
            ),
            current_round="opinion",
        ),
    )
]