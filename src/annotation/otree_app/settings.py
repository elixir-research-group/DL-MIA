import os

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=0.000, participation_fee=0.00, doc=""
)

SESSION_CONFIGS = [
    dict(
        name="query_intents_v2",
        display_name="Query intents (v2)",
        num_demo_participants=10,
        app_sequence=["query_intents_v2"],
    ),
]

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = "en"
# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = "USD"
USE_POINTS = True
ADMIN_USERNAME = os.environ.get("OTREE_ADMIN_USERNAME")
ADMIN_PASSWORD = os.environ.get("OTREE_ADMIN_PASSWORD")

ROOMS = [
    dict(
        name="study",
        display_name="Room for study",
        # participant_label_file='_rooms/your_study.txt',
        # use_secure_urls=True,
    ),
]

# don't share this with anybody.
SECRET_KEY = os.environ.get("SECRET_KEY")
SESSION_FIELDS = []
PARTICIPANT_FIELDS = []
