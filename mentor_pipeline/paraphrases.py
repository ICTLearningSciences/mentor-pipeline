#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
import csv
from dataclasses import asdict, dataclass, field
import logging
import os
import re
from typing import Dict, List, Union


def to_question_id(q: str) -> str:
    # result string will be lowercase, only alphanumeric, tokens separated by _, and no leading or trailing _
    return re.sub(
        "^[^a-zA-Z0-9]+",
        "",
        re.sub("[^a-zA-Z0-9]+$", "", re.sub("[^a-zA-Z0-9]+", "_", q.lower())),
    )


@dataclass
class QuestionParaphrases:
    question: str = ""
    paraphrases: List[str] = field(default_factory=lambda: [])

    def to_dict(self):
        return asdict(self)


@dataclass
class ParaphrasesByQuestion:
    questionParaphrasesById: Dict[str, QuestionParaphrases] = field(
        default_factory=lambda: {}
    )

    def __post_init__(self):
        self.questionParaphrasesById = {
            to_question_id(k): v
            if isinstance(v, QuestionParaphrases)
            else QuestionParaphrases(**v)
            for (k, v) in self.questionParaphrasesById.items()
        }

    def find_paraphrases(self, question: str) -> List[str]:
        qt = self.questionParaphrasesById.get(to_question_id(question))
        return (qt.paraphrases or []) if qt else []

    def to_dict(self):
        return asdict(self)


def load_paraphrases_by_question_from_list(
    question_paraphrases_list: List[Union[QuestionParaphrases, dict]]
) -> ParaphrasesByQuestion:
    xlist = [
        x if isinstance(x, QuestionParaphrases) else QuestionParaphrases(**x)
        for x in question_paraphrases_list
    ]
    return ParaphrasesByQuestion(
        **dict(questionParaphrasesById={to_question_id(x.question): x for x in xlist})
    )


def load_paraphrases_by_question_from_csv(
    question_paraphrases_csv: str,
    allow_file_not_exists: bool = False,
    warn_on_file_not_exists: bool = True,
) -> ParaphrasesByQuestion:
    if not os.path.isfile(question_paraphrases_csv):
        if allow_file_not_exists:
            if warn_on_file_not_exists:
                logging.warning(
                    f"no paraphrases_by_question csv file found at {question_paraphrases_csv}"
                )
            return ParaphrasesByQuestion()
        else:
            raise Exception(
                f"expected paraphrases_by_question csv file at {question_paraphrases_csv} (or pass allow_file_not_exists=True)"
            )
    with open(question_paraphrases_csv, "r", encoding="utf-8") as f:
        r = csv.reader(f)
        xlist = [
            QuestionParaphrases(
                question=x[0], paraphrases=[p for p in x[1:] if p]
            )  # topic list is delimited with |
            for i, x in enumerate(r)
            if i != 0 and len(x) >= 2  # skip header row and trailing/empty
        ]
        return ParaphrasesByQuestion(
            **dict(
                questionParaphrasesById={to_question_id(x.question): x for x in xlist}
            )
        )
