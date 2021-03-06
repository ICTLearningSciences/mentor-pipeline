#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
from dataclasses import dataclass, field
import os
from typing import List

import pandas as pd


COLS_CLASSIFIER_DATA: List[str] = ["ID", "topics", "text", "question"]
COLS_QUESTIONS_PARAPHRASES_ANSWERS: List[str] = [
    "Topics",
    "Helpers",
    "Mentor",
    "Question",
    "text",
]
COLS_PROMPTS_UTTERANCES: List[str] = ["Situation", "Mentor", "Utterance/Prompt"]
COLS_UTTERANCE_DATA: List[str] = ["ID", "utterance", "situation"]


@dataclass
class QuestionsParaphrasesAnswersRow:
    answer: str = ""
    helpers: str = ""
    mentor_id: str = ""
    question: str = ""
    topics: List[str] = field(default_factory=lambda: [])

    def to_row(self) -> List[str]:
        return [
            ",".join(self.topics) if self.topics else "",
            self.helpers or "",
            self.mentor_id or "",
            self.question or "",
            self.answer or "",
        ]


@dataclass
class ClassifierDataRow:
    ID: str = ""
    question: str = ""
    paraphrases: List[str] = field(default_factory=lambda: [])
    topics: List[str] = field(default_factory=lambda: [])
    text: str = ""

    def to_row(self) -> List[str]:
        q_and_p = [self.question] + (self.paraphrases or [])
        r = [self.ID, ",".join(self.topics or []), self.text, "\n".join(q_and_p)]
        return r


@dataclass
class ClassifierDataBuilder:
    data: List[ClassifierDataRow] = field(default_factory=lambda: [])

    def add_row(
        self,
        id: str = "",
        question: str = "",
        text: str = "",
        topics: List[str] = field(default_factory=lambda: []),
        paraphrases: List[str] = field(default_factory=lambda: []),
    ) -> None:
        self.data.append(  # pylint: disable=no-member
            ClassifierDataRow(
                ID=id,
                question=question,
                text=text,
                topics=topics,
                paraphrases=paraphrases,
            )
        )

    def to_data_frame(self) -> pd.DataFrame:
        return pd.DataFrame(
            [r.to_row() for r in self.data],  # pylint: disable=not-an-iterable
            columns=COLS_CLASSIFIER_DATA,
        )


@dataclass
class QuestionsParaphrasesAnswersBuilder:
    data: List[QuestionsParaphrasesAnswersRow] = field(default_factory=lambda: [])

    def add_row(
        self, question: str = "", answer: str = "", mentor_id: str = ""
    ) -> None:
        self.data.append(  # pylint: disable=no-member
            QuestionsParaphrasesAnswersRow(
                question=question, answer=answer, mentor_id=mentor_id
            )
        )

    def to_data_frame(self) -> pd.DataFrame:
        return pd.DataFrame(
            [r.to_row() for r in self.data],  # pylint: disable=not-an-iterable
            columns=COLS_QUESTIONS_PARAPHRASES_ANSWERS,
        )


@dataclass
class PromptsUtterancesRow:
    mentor_id: str = ""
    situation: str = ""
    utterance: str = ""

    def to_row(self) -> List[str]:
        return [self.situation, self.mentor_id, self.utterance]


@dataclass
class PromptsUtterancesBuilder:
    data: List[PromptsUtterancesRow] = field(default_factory=lambda: [])

    def add_row(
        self, mentor_id: str = "", situation: str = "", utterance: str = ""
    ) -> None:
        self.data.append(  # pylint: disable=no-member
            PromptsUtterancesRow(
                mentor_id=mentor_id, situation=situation, utterance=utterance
            )
        )

    def to_data_frame(self) -> pd.DataFrame:
        return pd.DataFrame(
            [r.to_row() for r in self.data],  # pylint: disable=not-an-iterable
            columns=COLS_PROMPTS_UTTERANCES,
        )


@dataclass
class UtteranceDataRow:
    ID: str = ""
    utterance: str = ""
    situation: str = ""

    def to_row(self) -> List[str]:
        return [self.ID, self.utterance, self.situation]


@dataclass
class UtteranceDataBuilder:
    data: List[UtteranceDataRow] = field(default_factory=lambda: [])

    def add_row(self, id: str = "", utterance: str = "", situation: str = "") -> None:
        self.data.append(  # pylint: disable=no-member
            UtteranceDataRow(ID=id, utterance=utterance, situation=situation)
        )

    def to_data_frame(self) -> pd.DataFrame:
        return pd.DataFrame(
            [r.to_row() for r in self.data],  # pylint: disable=not-an-iterable
            columns=COLS_UTTERANCE_DATA,
        )


def _add_file_if_dir(base_path, file_name: str) -> str:
    return os.path.join(base_path, file_name) if os.path.isdir(base_path) else base_path


def _load_csv(csv_path: str, file_name_default: str) -> pd.DataFrame:
    return pd.read_csv(_add_file_if_dir(csv_path, file_name_default)).fillna("")


def _write_csv(d: pd.DataFrame, csv_path: str, file_name_default: str) -> None:
    write_path = _add_file_if_dir(csv_path, file_name_default)
    os.makedirs(os.path.dirname(write_path), exist_ok=True)
    csv_str = d.fillna("").to_csv(
        index=False
    )  # to_csv can't see to overwrite an existing file even with mode='w'?
    with open(write_path, "w") as f:
        f.write(csv_str)


def load_classifier_data(csv_path: str) -> pd.DataFrame:
    return _load_csv(csv_path, "classifier_data.csv")


def load_questions_paraphrases_answers(csv_path: str) -> pd.DataFrame:
    return _load_csv(csv_path, "questions_paraphrases_answers.csv")


def load_prompts_utterances(csv_path: str) -> pd.DataFrame:
    return _load_csv(csv_path, "prompts_utterances.csv")


def load_utterance_data(csv_path: str) -> pd.DataFrame:
    return _load_csv(csv_path, "utterance_data.csv")


def write_classifier_data(d: pd.DataFrame, csv_path: str) -> None:
    _write_csv(d, csv_path, "classifier_data.csv")


def write_questions_paraphrases_answers(d: pd.DataFrame, csv_path: str) -> None:
    _write_csv(d, csv_path, "questions_paraphrases_answers.csv")


def write_prompts_utterances(d: pd.DataFrame, csv_path: str) -> None:
    _write_csv(d, csv_path, "prompts_utterances.csv")


def write_utterance_data(d: pd.DataFrame, csv_path: str) -> None:
    _write_csv(d, csv_path, "utterance_data.csv")
