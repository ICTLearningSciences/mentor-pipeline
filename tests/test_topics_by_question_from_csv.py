# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
from tempfile import mkdtemp
import os

import pytest

from mentor_pipeline.topics import (
    QuestionTopics,
    TopicsByQuestion,
    load_topics_by_question_from_csv,
    load_topics_by_question_from_list,
)


@pytest.mark.parametrize(
    "input_topics_by_question_csv_str,expected_topics",
    [
        (
            """Question,Topics
What is your name?,Background
What is your quest?,Background|Quests
What is your favorite color?,About Me
""",
            [
                QuestionTopics(question="What is your name?", topics=["Background"]),
                QuestionTopics(
                    question="What is your quest?", topics=["Background", "Quests"]
                ),
                QuestionTopics(
                    question="What is your favorite color?", topics=["About Me"]
                ),
            ],
        )
    ],
)
def test_load_topics_by_question_from_csv(
    input_topics_by_question_csv_str, expected_topics
):
    tmpdir = mkdtemp()
    csv_file = os.path.join(tmpdir, "topics_by_question.csv")
    with open(csv_file, "w") as f:
        f.write(input_topics_by_question_csv_str)
    expected_topics_by_question = load_topics_by_question_from_list(expected_topics)
    actual_topics_by_question = load_topics_by_question_from_csv(csv_file)
    assert expected_topics_by_question.to_dict() == actual_topics_by_question.to_dict()


def test_load_topics_by_question_raises_if_file_not_exists():
    expectedError: Exception = None
    try:
        load_topics_by_question_from_csv("/some/noneexisting/path.csv")
    except Exception as err:
        expectedError = err
    assert expectedError is not None


def test_load_topics_by_question_returns_empty_if_file_not_exist_but_arg():
    actual_topics_by_question = load_topics_by_question_from_csv(
        "/some/noneexisting/path.csv", allow_file_not_exists=True
    )
    expected_topics_by_question = TopicsByQuestion()
    assert expected_topics_by_question.to_dict() == actual_topics_by_question.to_dict()
