#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
from glob import glob
import os

import pandas as pd
import pytest
from unittest.mock import patch

from .helpers import (
    assert_utterance_asset_exists,
    MockAudioSlicer,
    MockTranscriptions,
    MockVideoToAudioConverter,
    assert_utterances_match_expected,
    copy_mentor_to_tmp,
    resource_root_mentors_for_test,
)
from mentor_pipeline.run import Pipeline
from mentor_pipeline.training_data import (
    load_classifier_data,
    load_questions_paraphrases_answers,
    load_prompts_utterances,
    load_utterance_data,
)
from mentor_pipeline.utterances import Utterance
from mentor_pipeline.utterance_asset_type import UTTERANCE_CAPTIONS


MENTOR_DATA_ROOT = resource_root_mentors_for_test(__file__)


@patch("mentor_pipeline.media_tools.video_to_audio")
@patch("mentor_pipeline.media_tools.slice_audio")
@patch("transcribe.init_transcription_service")
@pytest.mark.parametrize(
    "mentor_data_root,mentor_id",
    [(MENTOR_DATA_ROOT, "mentor-generates-all-data-files")],
)
def test_run_data_update_generates_all_data_files_for_a_mentor(
    mock_init_transcription_service,
    mock_slice_audio,
    mock_video_to_audio,
    mentor_data_root: str,
    mentor_id: str,
):
    _test_run_data_update(
        mock_init_transcription_service,
        mock_slice_audio,
        mock_video_to_audio,
        mentor_data_root,
        mentor_id,
    )


@patch("mentor_pipeline.media_tools.video_to_audio")
@patch("mentor_pipeline.media_tools.slice_audio")
@patch("transcribe.init_transcription_service")
@pytest.mark.parametrize(
    "mentor_data_root,mentor_id",
    [(MENTOR_DATA_ROOT, "mentor2-force-updates-transcripts")],
)
def test_run_data_update_force_updates_transcripts_when_flag_set(
    mock_init_transcription_service,
    mock_slice_audio,
    mock_video_to_audio,
    mentor_data_root: str,
    mentor_id: str,
):
    _test_run_data_update(
        mock_init_transcription_service,
        mock_slice_audio,
        mock_video_to_audio,
        mentor_data_root,
        mentor_id,
        force_update_transcripts=True,
    )


@patch("mentor_pipeline.media_tools.video_to_audio")
@patch("mentor_pipeline.media_tools.slice_audio")
@patch("transcribe.init_transcription_service")
@pytest.mark.parametrize(
    "mentor_data_root,mentor_id",
    [(MENTOR_DATA_ROOT, "mentor3-skips-utterances-with-exising-transcripts")],
)
def test_run_data_update_skips_utterances_with_existing_transcripts_by_default(
    mock_init_transcription_service,
    mock_slice_audio,
    mock_video_to_audio,
    mentor_data_root: str,
    mentor_id: str,
):
    _test_run_data_update(
        mock_init_transcription_service,
        mock_slice_audio,
        mock_video_to_audio,
        mentor_data_root,
        mentor_id,
    )


def _test_run_data_update(
    mock_init_transcription_service,
    mock_slice_audio,
    mock_video_to_audio,
    mentor_data_root: str,
    mentor_id: str,
    force_update_transcripts: bool = False,
):
    mpath = copy_mentor_to_tmp(mentor_id, mentor_data_root)
    mock_transcriptions = MockTranscriptions(mpath, mock_init_transcription_service)
    mock_transcriptions.mock_transcribe_result_and_callbacks()
    MockAudioSlicer(mock_slice_audio, create_dummy_output_files=True)
    MockVideoToAudioConverter(mock_video_to_audio, create_dummy_output_files=True)
    p = Pipeline(mentor_id, mpath.root_path_data_mentors)
    p.data_update(force_update_transcripts=force_update_transcripts)
    assert_utterances_match_expected(mpath)
    expected_questions_paraphrases_answers = load_questions_paraphrases_answers(
        mpath.get_mentor_data(os.path.join("expected_data"))
    )
    actual_questions_paraphrases_answers = (
        mpath.load_training_questions_paraphrases_answers()
    )
    pd.testing.assert_frame_equal(
        expected_questions_paraphrases_answers, actual_questions_paraphrases_answers
    )
    expected_prompts_utterances = load_prompts_utterances(
        mpath.get_mentor_data(os.path.join("expected_data"))
    )
    actual_prompts_utterances = mpath.load_training_prompts_utterances()
    pd.testing.assert_frame_equal(
        expected_prompts_utterances, actual_prompts_utterances
    )
    expected_utterance_data = load_utterance_data(
        mpath.get_mentor_data(os.path.join("expected_data"))
    )
    actual_utterance_data = mpath.load_training_utterance_data()
    pd.testing.assert_frame_equal(expected_utterance_data, actual_utterance_data)
    expected_classifier_data = load_classifier_data(
        mpath.get_mentor_data(os.path.join("expected_data"))
    )
    actual_classifier_data = mpath.load_training_classifier_data()
    pd.testing.assert_frame_equal(expected_classifier_data, actual_classifier_data)
    actual_utterances = mpath.load_utterances()
    expected_captions_file_list = glob(
        mpath.get_mentor_data(os.path.join("expected_captions", "*.vtt"))
    )
    assert len(expected_captions_file_list) > 0
    for expected_captions_file in expected_captions_file_list:
        uid = os.path.splitext(os.path.basename(expected_captions_file))[0]
        u = actual_utterances.find_by_id(uid)
        assert isinstance(
            u, Utterance
        ), f"expected to find an utterance with id {uid} in utterances.yaml data"
        assert_utterance_asset_exists(mpath, u, UTTERANCE_CAPTIONS)
        actual_captions_path = mpath.find_utterance_captions(u)
        with open(expected_captions_file, "r") as f_expected, open(
            actual_captions_path, "r"
        ) as f_actual:
            expected_captions = f_expected.read()
            actual_captions = f_actual.read()
            assert expected_captions == actual_captions
