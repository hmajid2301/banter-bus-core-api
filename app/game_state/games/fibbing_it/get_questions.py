import asyncio
import random

from app.clients.management_api.api.questions_api import AsyncQuestionsApi
from app.game_state.game_state_models import (
    FibbingItQuestion,
    FibbingItQuestionsState,
    FibbingItRounds,
)
from app.game_state.games.exceptions import InvalidGameRound
from app.player.player_models import Player


class GetQuestions:
    def __init__(self, question_client: AsyncQuestionsApi, players: list[Player], questions_per_round: int = 3) -> None:
        self.question_client = question_client
        self.players = players
        self.rounds = ["opinion", "likely", "free_form"]
        self.rounds_with_groups = ["opinion", "free_form"]
        self.questions_per_round = questions_per_round

    async def __call__(self) -> FibbingItQuestionsState:
        rounds_dict = await self._get_rounds()
        rounds = FibbingItRounds(**rounds_dict)
        return FibbingItQuestionsState(rounds=rounds, current_answers={})

    async def _get_rounds(self) -> dict[str, list[FibbingItQuestion]]:
        rounds_questions_map: dict[str, list[FibbingItQuestion]] = {"opinion": [], "likely": [], "free_form": []}
        for round_ in self.rounds:
            questions_in_round = await self._get_questions_for_round(round_)

            rounds_questions_map[round_] = questions_in_round
        return rounds_questions_map

    async def _get_questions_for_round(self, round_: str) -> list[FibbingItQuestion]:
        if round_ not in self.rounds_with_groups:
            return await self._get_questions_for_rounds_without_group(round_)
        return await self._get_questions_for_rounds_with_groups(round_)

    async def _get_questions_for_rounds_with_groups(self, round_: str) -> list[FibbingItQuestion]:
        questions_in_round: list[FibbingItQuestion] = []
        random_groups = await self.question_client.get_random_groups(
            game_name="fibbing_it", round=round_, limit=self.questions_per_round
        )
        # TODO: fix typing
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

    async def _get_questions_for_rounds_without_group(self, round_: str) -> list[FibbingItQuestion]:
        questions_in_round: list[FibbingItQuestion] = []
        random_questions = await self.question_client.get_random_questions(
            game_name="fibbing_it", round=round_, limit=self.questions_per_round
        )
        for question in random_questions:
            player_names = [player.nickname for player in self.players]
            fibbing_it_question = FibbingItQuestion(fibber_question="", question=question.content, answers=player_names)
            questions_in_round.append(fibbing_it_question)
        return questions_in_round
