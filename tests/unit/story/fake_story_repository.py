from typing import List

from app.story.story_exceptions import StoryExists, StoryNotFound
from app.story.story_models import Story
from app.story.story_repository import AbstractStoryRepository


class FakeStoryRepository(AbstractStoryRepository):
    def __init__(self, stories: List[Story]):
        self.stories = stories

    async def add(self, new_story: Story):
        for story in self.stories:
            if story.story_id == new_story.story_id:
                raise StoryExists("story already exists")
        else:
            self.stories.append(new_story)

    async def get(self, story_id: str) -> Story:
        for story in self.stories:
            if story.story_id == story_id:
                return story

        raise StoryNotFound("story not found")

    async def remove(self, story_id: str):
        story = await self.get(story_id=story_id)
        if not story:
            raise StoryNotFound("story not found")
        self.stories.remove(story)
