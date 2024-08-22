import csv
import os
import string
import sys
from collections import defaultdict
from pathlib import Path

from otree.api import *

doc = """
Given a query and relevant passages, select what information needs are satisfied.
"""


csv.field_size_limit(sys.maxsize)


def sanitize(s, allowed_chars=string.printable, max_len=None):
    return "".join(
        filter(lambda c: c in allowed_chars, s if max_len is None else s[:max_len])
    )


class C(BaseConstants):
    NAME_IN_URL = Path(__file__).parent.name
    PLAYERS_PER_GROUP = None
    COMPLETION_CODE = os.environ.get("COMPLETION_CODE")

    def _read(f, k, v):
        result = {}
        with open(f, encoding="utf-8", newline="") as fp:
            for row in csv.DictReader(fp, delimiter="\t"):
                result[row[k]] = row[v]
        return result

    QUERIES = _read(os.environ.get("EXP_QUERIES"), "q_id", "query")
    DOCUMENTS = _read(os.environ.get("EXP_DOCS"), "doc_id", "doc")

    MAPPING = defaultdict(list)
    with open(os.environ.get("EXP_MAPPING"), encoding="utf-8", newline="") as fp:
        for row in csv.DictReader(fp, delimiter="\t"):
            MAPPING[row["q_id"]].append(row["doc_id"])

    INTENT_CANDIDATES = defaultdict(list)
    with open(
        os.environ.get("EXP_INTENT_CANDIDATES"), encoding="utf-8", newline=""
    ) as fp:
        for row in csv.DictReader(fp, delimiter="\t"):
            INTENT_CANDIDATES[row["q_id"]].append(row["intent"])

    ALLOCATION = defaultdict(dict)
    with open(os.environ.get("EXP_DATA"), encoding="utf-8", newline="") as fp:
        for row in csv.DictReader(fp, delimiter="\t"):
            ALLOCATION[int(row["participant_id"])][int(row["round"])] = row["q_id"]

    NUM_PARTICIPANTS = len(ALLOCATION)
    NUM_ROUNDS = len(ALLOCATION[1])
    NUM_INTENT_FIELDS = int(os.environ.get("NUM_INTENT_FIELDS"))


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    nickname = models.StringField(label="Your (nick)name (optional):", blank=True)

    consent = models.BooleanField(
        label="I have read and understood the above text.",
        widget=widgets.CheckboxInput,
        blank=False,
    )

    result_assessments = models.LongStringField(blank=True)

    feedback = models.LongStringField(
        label="Please provide your feedback here:", blank=True
    )


for i in range(C.NUM_INTENT_FIELDS):
    setattr(Player, f"result_i{i}", models.LongStringField(blank=True))


class ConsentPage(Page):
    form_model = "player"
    form_fields = ["nickname", "consent"]

    @staticmethod
    def is_displayed(player):
        # populate input field
        player.nickname = player.participant.label
        return player.round_number == 1

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.nickname = sanitize(player.nickname)
        player.participant.label = player.nickname


class InstructionsPage(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1


class ItemPage(Page):
    form_model = "player"
    form_fields = ["result_assessments"] + [
        f"result_i{i}" for i in range(C.NUM_INTENT_FIELDS)
    ]

    @staticmethod
    def vars_for_template(player):
        q_id = C.ALLOCATION[
            # otree IDs start at one
            (player.participant.id_in_session - 1) % C.NUM_PARTICIPANTS
            + 1
        ][player.round_number]
        return {
            "query": C.QUERIES[q_id],
            "cur_round": player.round_number,
            "total_rounds": C.NUM_ROUNDS,
            "progress": (player.round_number - 1) / C.NUM_ROUNDS * 100,
            "passages": [
                # we might have a list of duplicate passages here, so only take the first one
                (p_id, C.DOCUMENTS[p_id.split(",")[0]])
                for p_id in C.MAPPING[q_id]
            ],
            "intents": [
                (
                    f"i{i}",
                    (
                        C.INTENT_CANDIDATES[q_id][i]
                        if i < len(C.INTENT_CANDIDATES[q_id])
                        else ""
                    ),
                )
                for i in range(C.NUM_INTENT_FIELDS)
            ],
        }

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        for field in [f"result_i{i}" for i in range(C.NUM_INTENT_FIELDS)]:
            val = getattr(player, field)
            setattr(player, field, sanitize(val))


class FeedbackPage(Page):
    form_model = "player"
    form_fields = ["feedback"]

    @staticmethod
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.feedback = sanitize(player.feedback)


class FinalPage(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS


page_sequence = [
    ConsentPage,
    InstructionsPage,
    ItemPage,
    FeedbackPage,
    FinalPage,
]
