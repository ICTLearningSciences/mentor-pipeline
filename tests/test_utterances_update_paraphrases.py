#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
import pytest

from mentor_pipeline.process import update_paraphrases
from mentor_pipeline.paraphrases import (
    load_paraphrases_by_question_from_list,
    QuestionParaphrases,
)
from mentor_pipeline.utterances import Utterance, utterance_map_from_list


@pytest.mark.parametrize(
    "input_utterances,input_paraphrases,expected_utterances",
    [
        (
            [
                Utterance(question="What is your name?", timeStart=0, timeEnd=1),
                Utterance(question="What is your quest?", timeStart=1, timeEnd=2),
                Utterance(
                    question="What is your favorite color?", timeStart=2, timeEnd=3
                ),
                Utterance(
                    question="What is the name of your cat?", timeStart=3, timeEnd=4
                ),
            ],
            [
                QuestionParaphrases(
                    question="what is your name", paraphrases=["Background"]
                ),
                QuestionParaphrases(
                    question="what is your quest", paraphrases=["Background", "Quests"]
                ),
                QuestionParaphrases(
                    question="what is your favorite color", paraphrases=["About Me"]
                ),
            ],
            [
                Utterance(
                    question="What is your name?",
                    paraphrases=["Background"],
                    timeStart=0,
                    timeEnd=1,
                ),
                Utterance(
                    question="What is your quest?",
                    paraphrases=["Background", "Quests"],
                    timeStart=1,
                    timeEnd=2,
                ),
                Utterance(
                    question="What is your favorite color?",
                    paraphrases=["About Me"],
                    timeStart=2,
                    timeEnd=3,
                ),
                Utterance(
                    question="What is the name of your cat?", timeStart=3, timeEnd=4
                ),
            ],
        )
    ],
)
def test_utterances_update_paraphrases(
    input_utterances, input_paraphrases, expected_utterances
):
    utterances = utterance_map_from_list(input_utterances)
    paraphrases = load_paraphrases_by_question_from_list(input_paraphrases)
    actual_utterances = update_paraphrases(utterances, paraphrases)
    assert (
        utterance_map_from_list(expected_utterances).to_dict()
        == actual_utterances.to_dict()
    )
