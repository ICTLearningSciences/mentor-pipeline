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
class QuestionTopics:
    question: str = ""
    topics: List[str] = field(default_factory=lambda: [])

    def to_dict(self):
        return asdict(self)


@dataclass
class TopicsByQuestion:
    questionsTopicsById: Dict[str, QuestionTopics] = field(default_factory=lambda: {})

    def __post_init__(self):
        self.questionsTopicsById = {
            to_question_id(k): v
            if isinstance(v, QuestionTopics)
            else QuestionTopics(**v)
            for (k, v) in self.questionsTopicsById.items()
        }

    def add_question_topics(self, question: str, topics: List[str]) -> None:
        self.questionsTopicsById[to_question_id(question)] = QuestionTopics(
            question=question, topics=sorted(topics)
        )

    def find_topics(self, question: str) -> List[str]:
        qt = self.questionsTopicsById.get(to_question_id(question))
        return (qt.topics or []) if qt else []

    def get_question_topics(self) -> List[QuestionTopics]:
        return [
            self.questionsTopicsById[qid]
            for qid in sorted(self.questionsTopicsById.keys())
        ]

    def to_dict(self):
        return asdict(self)


def load_topics_by_question_from_list(
    question_topics_list: List[Union[QuestionTopics, dict]]
) -> TopicsByQuestion:
    xlist = [
        x if isinstance(x, QuestionTopics) else QuestionTopics(**x)
        for x in question_topics_list
    ]
    return TopicsByQuestion(
        **dict(questionsTopicsById={to_question_id(x.question): x for x in xlist})
    )


def load_topics_by_question_from_csv(
    question_topics_csv: str,
    allow_file_not_exists: bool = False,
    warn_on_file_not_exists: bool = True,
) -> TopicsByQuestion:
    if not os.path.isfile(question_topics_csv):
        if allow_file_not_exists:
            if warn_on_file_not_exists:
                logging.warning(
                    f"no topics_by_question csv file found at {question_topics_csv}"
                )
            return TopicsByQuestion()
        else:
            raise Exception(
                f"expected topics_by_question csv file at {question_topics_csv} (or pass allow_file_not_exists=True)"
            )
    with open(question_topics_csv, "r", encoding="utf-8") as f:
        r = csv.reader(f)
        xlist = [
            QuestionTopics(
                question=x[0], topics=x[1].split("|")
            )  # topic list is delimited with |
            for i, x in enumerate(r)
            if i != 0 and len(x) >= 2  # skip header row and trailing/empty
        ]
        return TopicsByQuestion(
            **dict(questionsTopicsById={to_question_id(x.question): x for x in xlist})
        )


def write_topics_by_question_to_csv(
    tbq: TopicsByQuestion, question_topics_csv: str
) -> None:
    try:
        os.makedirs(os.path.dirname(question_topics_csv), exist_ok=True)
        logging.warning(f"write_topics_by_question_to_csv to {question_topics_csv}")
        with open(question_topics_csv, "w", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["Questions", "Topics"])
            for qts in tbq.get_question_topics():
                logging.warning(f"WHAT IS QTS? {qts}")
                w.writerow([qts.question, "|".join(qts.topics)])
    except Exception as root_err:
        logging.warning(f"error writing {question_topics_csv}: {root_err}")
