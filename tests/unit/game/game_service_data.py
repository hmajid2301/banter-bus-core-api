import factory

get_game_name_data = [
    (
        {
            "size": 2,
            "name": factory.Sequence(lambda n: ["quibly", "fibbing_it"][n % 2]),
            "enabled": factory.sequence(lambda n: True),
        },
        "all",
        ["quibly", "fibbing_it"],
    ),
    (
        {
            "size": 2,
            "name": factory.Sequence(lambda n: ["quibly", "fibbing_it"][n % 2]),
            "enabled": factory.sequence(lambda n: True),
        },
        "enabled",
        ["quibly", "fibbing_it"],
    ),
    (
        {
            "size": 2,
            "name": factory.Sequence(lambda n: ["quibly", "fibbing_it"][n % 2]),
            "enabled": factory.sequence(lambda n: True),
        },
        "disabled",
        [],
    ),
    (
        {
            "size": 2,
            "name": factory.Sequence(lambda n: ["quibly", "fibbing_it"][n % 2]),
            "enabled": factory.sequence(lambda n: False),
        },
        "disabled",
        ["quibly", "fibbing_it"],
    ),
    (
        {
            "size": 2,
            "name": factory.Sequence(lambda n: ["quibly", "fibbing_it"][n % 2]),
            "enabled": factory.sequence(lambda n: [True, False][n % 2]),
        },
        "all",
        ["quibly", "fibbing_it"],
    ),
    (
        {
            "size": 2,
            "name": factory.Sequence(lambda n: ["quibly", "fibbing_it"][n % 2]),
            "enabled": factory.sequence(lambda n: [True, False][n % 2]),
        },
        "disabled",
        ["fibbing_it"],
    ),
    (
        {
            "size": 2,
            "name": factory.Sequence(lambda n: ["quibly", "fibbing_it"][n % 2]),
            "enabled": factory.sequence(lambda n: [True, False][n % 2]),
        },
        "enabled",
        ["quibly"],
    ),
]


enable_game_data = [
    (
        {
            "size": 2,
            "name": factory.Sequence(lambda n: ["quibly", "fibbing_it"][n % 2]),
            "enabled": factory.sequence(lambda n: False),
        },
        "quibly",
    ),
    (
        {
            "size": 2,
            "name": factory.Sequence(lambda n: ["quibly", "fibbing_it"][n % 2]),
            "enabled": factory.sequence(lambda n: True),
        },
        "quibly",
    ),
    (
        {
            "size": 2,
            "name": factory.Sequence(lambda n: ["quibly", "fibbing_it"][n % 2]),
            "enabled": factory.sequence(lambda n: [True, False][n % 2]),
        },
        "fibbing_it",
    ),
    (
        {
            "size": 2,
            "name": factory.Sequence(lambda n: ["quibly", "fibbing_it"][n % 2]),
            "enabled": factory.sequence(lambda n: [True, False][n % 2]),
        },
        "quibly",
    ),
]

disable_game_data = [
    (
        {
            "size": 2,
            "name": factory.Sequence(lambda n: ["quibly", "fibbing_it"][n % 2]),
            "enabled": factory.sequence(lambda n: True),
        },
        "quibly",
    ),
    (
        {
            "size": 2,
            "name": factory.Sequence(lambda n: ["quibly", "fibbing_it"][n % 2]),
            "enabled": factory.sequence(lambda n: False),
        },
        "quibly",
    ),
    (
        {
            "size": 2,
            "name": factory.Sequence(lambda n: ["quibly", "fibbing_it"][n % 2]),
            "enabled": factory.sequence(lambda n: [True, False][n % 2]),
        },
        "quibly",
    ),
    (
        {
            "size": 2,
            "name": factory.Sequence(lambda n: ["quibly", "fibbing_it"][n % 2]),
            "enabled": factory.sequence(lambda n: [True, False][n % 2]),
        },
        "fibbing_it",
    ),
]

update_enable_status_data = [
    (True),
    (False),
]
