import factory
import factory.fuzzy

from app.game.game_models import Game

game_names = {"quibly": "Quibly", "fibbing_it": "Fibbing IT!", "drawlosseum": "drawlosseum"}


class GameFactory(factory.Factory):
    class Meta:
        model = Game

    name = factory.fuzzy.FuzzyChoice(game_names.keys())
    rules_url = factory.Faker("url")
    enabled = factory.Faker("pybool")
    description = factory.Faker("sentence", nb_words=4)
    display_name = factory.LazyAttribute(lambda factory_item: game_names[factory_item.name])
