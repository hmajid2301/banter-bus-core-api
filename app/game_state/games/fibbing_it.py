import asyncio
import random
from typing import Dict, List, Union

from app.clients.management_api.api.questions_api import AsyncQuestionsApi
from app.game_state.game_state_models import (
    FibbingItQuestion,
    FibbingItQuestionsState,
    FibbingItRounds,
    FibbingItState,
)
from app.game_state.games.exceptions import InvalidGameRound
from app.game_state.games.game import AbstractGame
from app.player.player_models import Player


class FibbingIt(AbstractGame):
    def __init__(self, questions_per_round: int = 3) -> None:
        self.questions_per_round_index = questions_per_round - 1
        self.rounds = ["opinion", "likely", "free_form"]
        self.rounds_with_groups = ["opinion", "free_form"]

    async def get_starting_state(self, question_client: AsyncQuestionsApi, players: List[Player]) -> FibbingItState:
        first_faker = random.choice(players)
        get_questions = GetQuestions(question_client=question_client, players=players)
        questions = await get_questions()
        starting_state = FibbingItState(
            current_faker=first_faker.player_id, questions_to_show=questions, current_round=self.rounds[0]
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

    async def get_next_question(
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


class GetQuestions:
    def __init__(self, question_client: AsyncQuestionsApi, players: List[Player]) -> None:
        self.question_client = question_client
        self.players = players
        self.rounds = ["opinion", "likely", "free_form"]
        self.rounds_with_groups = ["opinion", "free_form"]

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
        random_groups = await self.question_client.get_random_groups(game_name="fibbing_it", round=round_, limit=3)
        questions_in_group = await asyncio.gather(
            *[
                self.question_client.get_random_questions(game_name="fibbing_it", round=round_, group_name=random_group)
                for random_group in random_groups.groups
            ]
        )

        for p in questions_in_group:
            if round_ == "opinion":
                questions_content = [question.content for question in p if question.type == "question"]
                answers_content = [answer.content for answer in p if answer.type == "answer"]
                faker_question, real_question = random.sample(questions_content, k=2)
                question = FibbingItQuestion(
                    faker_question=faker_question, question=real_question, answers=answers_content
                )
            elif round_ == "free_form":
                questions_content = [question.content for question in p]
                faker_question, real_question = random.sample(questions_content, k=2)
                question = FibbingItQuestion(faker_question=faker_question, question=real_question)
            else:
                raise InvalidGameRound(f"unexpected game round {round_}")

            questions_in_round.append(question)

        return questions_in_round

    async def _get_questions_for_rounds_without_group(self, round_: str) -> List[FibbingItQuestion]:
        questions_in_round: List[FibbingItQuestion] = []
        random_questions = await self.question_client.get_random_questions(
            game_name="fibbing_it", round=round_, limit=3
        )
        for question in random_questions:
            player_names = [player.nickname for player in self.players]
            question = FibbingItQuestion(faker_question="", question=question.content, answers=player_names)
            questions_in_round.append(question)
        return questions_in_round
