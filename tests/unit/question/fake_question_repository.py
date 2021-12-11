import random
from typing import List, Optional, Set

from app.question.question_exceptions import QuestionExistsException, QuestionNotFound
from app.question.question_models import NewQuestion, Question
from app.question.question_repository import AbstractQuestionRepository


class FakeQuestionRepository(AbstractQuestionRepository):
    def __init__(self, questions: List[Question]):
        self.questions = questions

    async def add(self, new_question: Question):
        for question in self.questions:
            if question.question_id == new_question.question_id:
                raise QuestionExistsException("question already exists")
        else:
            self.questions.append(new_question)

    async def get(self, question_id: str) -> Question:
        for question in self.questions:
            if question.question_id == question_id:
                return question
        else:
            raise QuestionNotFound("question not found")

    async def remove(self, question_id: str):
        question = await self.get(question_id=question_id)
        self.questions.remove(question)

    async def does_question_exist(self, new_question: NewQuestion) -> bool:
        for question in self.questions:
            if (
                question.round_ == new_question.round_
                and new_question.game_name == question.game_name
                and question.group == new_question.group
                and new_question.language_code in question.content
                and question.content[new_question.language_code] == new_question.content
            ):
                return True
        else:
            return False

    async def update_enable_status(self, question_id: str, enabled: bool) -> Question:
        for question in self.questions:
            if question.question_id == question_id:
                question.enabled = enabled
                return question
        else:
            raise QuestionNotFound("question not found")

    async def add_translation(self, question_id: str, language_code: str, content: str) -> Question:
        question = await self.get(question_id=question_id)
        if language_code in question.content:
            raise QuestionExistsException("language code already ecists for question")
        question.content[language_code] = content
        return question

    async def remove_translation(self, question_id: str, language_code: str):
        question = await self.get(question_id=question_id)
        try:
            del question.content[language_code]
        except KeyError:
            raise QuestionNotFound(f"{language_code=} not found in question {question_id=}")

    async def get_ids(
        self,
        game_name: str,
        limit: int,
        cursor: Optional[str] = None,
    ) -> List[str]:
        question_ids: List[str] = []
        at_cursor = False if cursor else True
        q = [question for question in self.questions if question.game_name == game_name]
        for question in q:
            if not at_cursor and question.question_id == cursor:
                at_cursor = True
                continue
            if at_cursor:
                question_ids.append(question.question_id)

            if len(question_ids) == limit:
                break

        return question_ids

    async def get_random(
        self,
        game_name: str,
        round_: str,
        language_code: str,
        limit: int = 5,
    ) -> List[Question]:
        questions: List[Question] = []
        for question in self.questions:
            if question.game_name == game_name and question.round_ == round_ and language_code in question.content:
                questions.append(question)

        num_of_questions = min(len(questions), limit)
        random_questions = random.sample(questions, k=num_of_questions)
        return random_questions

    async def get_questions_in_group(
        self, game_name: str, round_: str, language_code: str, group_name: str
    ) -> List[Question]:
        questions: List[Question] = []
        for question in self.questions:
            if (
                question.group
                and question.group.name == group_name
                and question.game_name == game_name
                and question.round_ == round_
                and language_code in question.content
            ):
                questions.append(question)
        return questions

    async def get_groups(self, game_name: str, round_: str) -> List[str]:
        groups: Set[str] = set()
        for question in self.questions:
            if question.game_name == game_name and question.round_ == round_:
                if question.group:
                    groups.add(question.group.name)
        return list(groups)
