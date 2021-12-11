from typing import List

from app.game.game_models import Game

games: List[Game] = [
    Game(
        **{
            "name": "quibly",
            "rules_url": "https://gitlab.com/banter-bus/banter-bus-server/-/wikis/docs/rules/quibly",
            "enabled": True,
            "description": "A game about quibbing.",
            "display_name": "Quibly",
        }
    ),
    Game(
        **{
            "name": "fibbing_it",
            "rules_url": "https://gitlab.com/banter-bus/banter-bus-server/-/wikis/docs/rules/fibbing_it",
            "enabled": True,
            "description": "A game about lying.",
            "display_name": "Fibbing IT!",
        }
    ),
    Game(
        **{
            "name": "drawlosseum",
            "rules_url": "https://google.com/drawlosseum",
            "enabled": False,
            "description": "A game about drawing.",
            "display_name": "Drawlosseum",
        }
    ),
]
