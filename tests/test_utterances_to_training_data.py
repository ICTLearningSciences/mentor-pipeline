# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
import pytest

import pandas as pd

from .helpers import copy_mentor_to_tmp, resource_root_mentors_for_test
from mentor_pipeline.process import utterances_to_training_data

COLS_QUESTIONS_PARAPHRASES_ANSWERS = ["Topics", "Helpers", "Mentor", "Question", "text"]


MENTOR_DATA_ROOT = resource_root_mentors_for_test(__file__)


@pytest.mark.parametrize("mentor_root,mentor_id", [(MENTOR_DATA_ROOT, "mentor1")])
def test_it_builds_training_data_from_utterances(mentor_root: str, mentor_id: str):
    _test_it_builds_training_data_from_utterances(mentor_root, mentor_id)


# @patch("logging.warning")
# @pytest.mark.parametrize(
#     "mentor_root,mentor_id,missing_utterance_types",
#     [
#         (
#             MENTOR_DATA_ROOT,
#             "mentor_has_no_utterances",
#             ["_FEEDBACK_", "_INTRO_", "_OFF_TOPIC_", "_PROMPT_", "_REPEAT_"],
#         ),
#         (
#             MENTOR_DATA_ROOT,
#             "mentor_has_missing_utterance_types_intro_and_feedback",
#             ["_FEEDBACK_", "_INTRO_"],
#         ),
#     ],
# )
# def test_it_builds_training_data_but_logs_a_warning_when_mentor_missing_utterances_types(
#     mockLoggingWarning, mentor_root: str, mentor_id: str, missing_utterance_types
# ):
#     _test_it_builds_training_data_from_question_and_answer_transcripts(
#         mentor_root, mentor_id
#     )
#     mockLoggingWarning.assert_called_once_with(
#         f"no transcripts found for mentor {mentor_id} with these utterance types: {missing_utterance_types}"
#     )


# @patch("pandas.DataFrame.to_csv")
# @pytest.mark.parametrize("mentor_root,mentor_id", [(MENTOR_DATA_ROOT, "mentor_1")])
# def test_it_writes_output_files_to_expected_paths(
#     mockPandasToCsv, mentor_root: str, mentor_id: str
# ):
#     transcripts_to_training_data(mentor_id, data_dir=mentor_root)
#     mockPandasToCsv.assert_has_calls(
#         [
#             call(
#                 os.path.join(
#                     mentor_root,
#                     f"data/mentors/{mentor_id}/data/questions_paraphrases_answers.csv",
#                 ),
#                 index=False,
#                 mode="w",
#             ),
#             call(
#                 os.path.join(
#                     mentor_root,
#                     f"data/mentors/{mentor_id}/data/prompts_utterances.csv",
#                 ),
#                 index=False,
#                 mode="w",
#             ),
#         ]
#     )


def _test_it_builds_training_data_from_utterances(mentor_root: str, mentor_id: str):
    mp = copy_mentor_to_tmp(mentor_id, mentor_root)
    utterances = mp.load_utterances()
    training_data = utterances_to_training_data(utterances)
    # expected_questions_paraphrases_answers = pd.read_csv(
    #     mp.get_mentor_data("expected_questions_paraphrases_answers.csv")
    # ).fillna("")
    # pd.testing.assert_frame_equal(
    #     expected_questions_paraphrases_answers,
    #     training_data.questions_paraphrases_answers,
    # )
    # expected_prompts_utterances = pd.read_csv(
    #     mp.get_mentor_data("expected_prompts_utterances.csv")
    # ).fillna("")
    # pd.testing.assert_frame_equal(
    #     expected_prompts_utterances, training_data.prompts_utterances
    # )
    expected_classifier_data = pd.read_csv(
        mp.get_mentor_data("expected_classifier_data.csv")
    ).fillna("")
    pd.testing.assert_frame_equal(
        expected_classifier_data, training_data.classifier_data
    )
    expected_utterance_data = pd.read_csv(
        mp.get_mentor_data("expected_utterance_data.csv")
    ).fillna("")
    pd.testing.assert_frame_equal(expected_utterance_data, training_data.utterance_data)
