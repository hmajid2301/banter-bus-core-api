import random
from datetime import datetime

from app.clients.management_api.api.questions_api import AsyncQuestionsApi
from app.game_state.game_state_exceptions import (
    ActionNotTimedOut,
    ActionTimedOut,
    InvalidGameState,
    NoAnswersFound,
)
from app.game_state.game_state_models import (
    DrawlossuemState,
    FibbingActions,
    FibbingItQuestion,
    FibbingItState,
    GameState,
    QuiblyState,
)
from app.game_state.games.exceptions import InvalidAction, InvalidAnswer
from app.game_state.games.fibbing_it.get_questions import GetQuestions
from app.game_state.games.game import AbstractGame
from app.player.player_models import Player


class FibbingIt(AbstractGame):
    def __init__(
        self, questions_per_round: int = 3, rounds_timer_map: dict[FibbingActions, dict[str, int]] | None = None
    ) -> None:
        self.questions_per_round_index = questions_per_round - 1
        self.rounds = ["opinion", "likely", "free_form"]
        self.rounds_with_groups = ["opinion", "free_form"]

        if not rounds_timer_map:
            self.round_timer_map = {
                FibbingActions.show_question: {"likely": 30, "opinion": 45, "free_form": 60},
                FibbingActions.submit_answers: {"likely": 30, "opinion": 30, "free_form": 30},
                FibbingActions.vote_on_fibber: {"likely": 60, "opinion": 60, "free_form": 60},
            }

    async def get_starting_state(self, question_client: AsyncQuestionsApi, players: list[Player]) -> FibbingItState:
        first_fibber = random.choice(players)
        get_questions = GetQuestions(
            question_client=question_client, players=players, questions_per_round=self.questions_per_round_index + 1
        )
        questions = await get_questions()
        return FibbingItState(
            current_fibber_id=first_fibber.player_id, questions=questions, current_round=self.rounds[0]
        )

    async def update_question_state(
        self, current_state: FibbingItState | QuiblyState | DrawlossuemState
    ) -> FibbingItState | None:
        current_state = FibbingItState(**current_state.dict())
        question_state = current_state.questions

        if question_state.question_nb == self.questions_per_round_index:
            round_index = self.rounds.index(current_state.current_round)
            if round_index == 2:
                return None

            new_round = self.rounds[round_index + 1]
            current_state.current_round = new_round
            question_state.question_nb = 0
        else:
            question_state.question_nb += 1

        new_state = current_state
        new_state.questions = question_state
        return new_state

    def get_next_question(
        self, current_state: FibbingItState | QuiblyState | DrawlossuemState
    ) -> FibbingItQuestion | None:
        current_state = FibbingItState(**current_state.dict())
        current_round = current_state.current_round
        current_question_state = current_state.questions
        if (current_round == "free_form") and (current_question_state.question_nb == self.questions_per_round_index):
            return None

        if current_round == "opinion":
            questions = current_question_state.rounds.opinion
        elif current_round == "likely":
            questions = current_question_state.rounds.likely
        else:
            questions = current_question_state.rounds.free_form

        question = questions[current_question_state.question_nb]
        return question

    def get_timer(self, current_round: str, action: FibbingActions) -> int:  # type: ignore[override]
        return self.round_timer_map[action][current_round]

    def has_round_changed(
        self, current_state: FibbingItState | QuiblyState | DrawlossuemState, old_round: str, new_round: str
    ) -> bool:
        current_state = FibbingItState(**current_state.dict())
        round_changed = False
        if current_state.current_round == "opinion" and current_state.questions.question_nb == 0:
            round_changed = True
        elif old_round != new_round:
            round_changed = True
        return round_changed

    def get_next_action(self, current_action: str) -> FibbingActions:
        next_action_map = {
            FibbingActions.show_question.value: FibbingActions.submit_answers,
            FibbingActions.submit_answers.value: FibbingActions.vote_on_fibber,
            FibbingActions.vote_on_fibber.value: FibbingActions.show_question,
        }
        next_action = next_action_map[current_action]
        return next_action

    def submit_answers(
        self, game_state: GameState, player_ids: list[str], player_id: str, answer: str
    ) -> FibbingItState:
        if not game_state.state or not game_state.action == FibbingActions.submit_answers:
            raise InvalidAction(
                f"expected action to be {FibbingActions.submit_answers.value}, current action {game_state.action.value}"
            )

        now = datetime.now()
        if not game_state.action_completed_by:
            raise InvalidGameState("expected game_state.action_completed_by to exist")
        elif game_state.action_completed_by <= now:
            raise ActionTimedOut(
                msg="cannot complete action out of time", now=now, completed_by=game_state.action_completed_by
            )

        state = FibbingItState(**game_state.state.dict())
        if state.current_round == "free_form" and len(answer) > 250:
            raise InvalidAnswer("invalid answer too long")
        elif state.current_round == "opinion":
            question = self.get_next_question(current_state=state)
            if (question and question.answers) and not (answer in question.answers):
                raise InvalidAnswer("invalid answer for round opinion")
        elif state.current_round == "likely" and answer not in player_ids:
            raise InvalidAnswer("invalid answer for round likely")

        state.questions.current_answers[player_id] = answer
        return state

    def select_random_answer(self, game_state: GameState, player_ids: list[str]) -> FibbingItState:
        if not game_state.state or not game_state.action == FibbingActions.submit_answers:
            raise InvalidAction(
                f"expected action to be {FibbingActions.submit_answers.value}, current action {game_state.action.value}"
            )

        now = datetime.now()
        if not game_state.action_completed_by:
            raise InvalidGameState("expected game_state.action_completed_by to exist")
        elif not game_state.action_completed_by >= now:
            raise ActionNotTimedOut("cannot complete action is not yet out of time")

        state = FibbingItState(**game_state.state.dict())
        player_answers = state.questions.current_answers
        for player_id in player_ids:
            if not player_answers.get(player_id):
                if state.current_round == "free_form":
                    player_answers[player_id] = ""
                elif state.current_round in ["likely", "opinion"]:
                    question = self.get_next_question(current_state=state)
                    if not question or not question.answers:
                        raise NoAnswersFound("no answers found for question")
                    player_answers[player_id] = random.choice(question.answers)
        return state

    def get_player_answers(self, state: FibbingItState, player_map: dict[str, str]) -> dict[str, str]:
        current_answers = state.questions.current_answers
        player_answers = {nickname: current_answers[player_id] for player_id, nickname in player_map.items()}
        return player_answers
