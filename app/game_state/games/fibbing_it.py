import asyncio
import random
from typing import Dict, List, Optional, Union

from app.clients.management_api.api.questions_api import AsyncQuestionsApi
from app.game_state.game_state_models import (
    FibbingActions,
    FibbingItQuestion,
    FibbingItQuestionsState,
    FibbingItRounds,
    FibbingItState,
)
from app.game_state.games.exceptions import InvalidGameRound
from app.game_state.games.game import AbstractGame
from app.player.player_models import Player


class FibbingIt(AbstractGame):
    def __init__(self, questions_per_round: int = 3, rounds_timer_map: Optional[dict] = None) -> None:
        self.questions_per_round_index = questions_per_round - 1
        self.rounds = ["opinion", "likely", "free_form"]
        self.rounds_with_groups = ["opinion", "free_form"]

        if not rounds_timer_map:
            self.round_timer_map = {
                FibbingActions.show_question: {"likely": 30, "opinion": 45, "free_form": 60},
                FibbingActions.submit_answers: {"likely": 30, "opinion": 30, "free_form": 30},
            }

    async def get_starting_state(self, question_client: AsyncQuestionsApi, players: List[Player]) -> FibbingItState:
        first_fibber = random.choice(players)
        get_questions = GetQuestions(
            question_client=question_client, players=players, questions_per_round=self.questions_per_round_index + 1
        )
        questions = await get_questions()
        starting_state = FibbingItState(
            current_fibber_sid=first_fibber.latest_sid, questions_to_show=questions, current_round=self.rounds[0]
        )
        return starting_state

    async def update_question_state(self, current_state: FibbingItState) -> Union[FibbingItState, None]:
        question_state = current_state.questions_to_show

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
        new_state.questions_to_show = question_state
        return new_state

    def get_next_question(
        self,
        current_state: FibbingItState,
    ) -> Union[FibbingItQuestion, None]:
        current_round = current_state.current_round
        current_question_state = current_state.questions_to_show
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

    def get_timer(self, current_state: FibbingItState, prev_action: FibbingActions) -> int:  # type: ignore[override]
        timer = self.round_timer_map[prev_action][current_state.current_round]
        return timer

    def has_round_changed(self, current_state: FibbingItState, old_round: str, new_round: str) -> bool:
        round_changed = False
        if current_state.current_round == "opinion" and current_state.questions_to_show.question_nb == 0:
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


class GetQuestions:
    def __init__(self, question_client: AsyncQuestionsApi, players: List[Player], questions_per_round: int = 3) -> None:
        self.question_client = question_client
        self.players = players
        self.rounds = ["opinion", "likely", "free_form"]
        self.rounds_with_groups = ["opinion", "free_form"]
        self.questions_per_round = questions_per_round

    async def __call__(self) -> FibbingItQuestionsState:
        rounds_dict = await self._get_rounds()
        rounds = FibbingItRounds(**rounds_dict)
        fibbing_it_state = FibbingItQuestionsState(rounds=rounds, current_answers=[])
        return fibbing_it_state

    async def _get_rounds(self) -> Dict[str, List[FibbingItQuestion]]:
        rounds_questions_map: Dict[str, List[FibbingItQuestion]] = {"opinion": [], "likely": [], "free_form": []}
        for round_ in self.rounds:
            questions_in_round = await self._get_questions_for_round(round_)

            rounds_questions_map[round_] = questions_in_round
        return rounds_questions_map

    async def _get_questions_for_round(self, round_: str) -> List[FibbingItQuestion]:
        questions_in_round: List[FibbingItQuestion] = []
        if round_ in self.rounds_with_groups:
            questions_in_round = await self._get_questions_for_rounds_with_groups(round_)
        else:
            questions_in_round = await self._get_questions_for_rounds_without_group(round_)
        return questions_in_round

    async def _get_questions_for_rounds_with_groups(self, round_: str) -> List[FibbingItQuestion]:
        questions_in_round: List[FibbingItQuestion] = []
        random_groups = await self.question_client.get_random_groups(
            game_name="fibbing_it", round=round_, limit=self.questions_per_round
        )
        questions_in_group = await asyncio.gather(
            *[
                self.question_client.get_random_questions(game_name="fibbing_it", round=round_, group_name=random_group)
                for random_group in random_groups.groups
            ]
        )

        for question_group in questions_in_group:
            if round_ == "opinion":
                questions_content = [question.content for question in question_group if question.type == "question"]
                answers_content = [answer.content for answer in question_group if answer.type == "answer"]
                fibber_question, real_question = random.sample(questions_content, k=2)
                question = FibbingItQuestion(
                    fibber_question=fibber_question, question=real_question, answers=answers_content
                )
            elif round_ == "free_form":
                questions_content = [question.content for question in question_group]
                fibber_question, real_question = random.sample(questions_content, k=2)
                question = FibbingItQuestion(fibber_question=fibber_question, question=real_question)
            else:
                raise InvalidGameRound(f"unexpected game round {round_}")

            questions_in_round.append(question)

        return questions_in_round

    async def _get_questions_for_rounds_without_group(self, round_: str) -> List[FibbingItQuestion]:
        questions_in_round: List[FibbingItQuestion] = []
        random_questions = await self.question_client.get_random_questions(
            game_name="fibbing_it", round=round_, limit=self.questions_per_round
        )
        for question in random_questions:
            player_names = [player.nickname for player in self.players]
            question = FibbingItQuestion(fibber_question="", question=question.content, answers=player_names)
            questions_in_round.append(question)
        return questions_in_round
