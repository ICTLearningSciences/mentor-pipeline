# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
import pytest
from unittest.mock import patch

from mentor_pipeline.process import update_transcripts
import transcribe
from mentor_pipeline.utterances import utterances_from_yaml

from .helpers import (
    MockTranscriptions,
    copy_mentor_to_tmp,
    resource_root_mentors_for_test,
)

MENTOR_DATA_ROOT = resource_root_mentors_for_test(__file__)


@patch.object(transcribe, "init_transcription_service")
@pytest.mark.parametrize("mentor_data_root,mentor_id", [(MENTOR_DATA_ROOT, "mentor1")])
def test_it_fills_in_transcripts_on_utterance_data(
    mock_init_transcription_service, mentor_data_root: str, mentor_id: str
):
    _test_utterances_update_transcripts(
        mock_init_transcription_service, mentor_data_root, mentor_id
    )


@patch.object(transcribe, "init_transcription_service")
@pytest.mark.parametrize(
    "mentor_data_root,mentor_id", [(MENTOR_DATA_ROOT, "mentor2-writes-on-update")]
)
def test_it_writes_transcriptions_to_utterances_on_each_update_callback(
    mock_init_transcription_service, mentor_data_root: str, mentor_id: str
):
    _test_utterances_update_transcripts(
        mock_init_transcription_service, mentor_data_root, mentor_id, test_logging=True
    )


@patch.object(transcribe, "init_transcription_service")
@pytest.mark.parametrize(
    "mentor_data_root,mentor_id",
    [(MENTOR_DATA_ROOT, "mentor3-skips-utterances-with-transcripts")],
)
def test_it_skips_utterances_with_existing_transcripts(
    mock_init_transcription_service, mentor_data_root: str, mentor_id: str
):
    _test_utterances_update_transcripts(
        mock_init_transcription_service, mentor_data_root, mentor_id, test_logging=True
    )


@patch.object(transcribe, "init_transcription_service")
@pytest.mark.parametrize(
    "mentor_data_root,mentor_id",
    [
        (
            MENTOR_DATA_ROOT,
            "mentor4-force-updates-utterances-with-existing-transcripts-when-flag-set",
        )
    ],
)
def test_it_force_updates_utterances_with_existing_transcripts_when_flag_set(
    mock_init_transcription_service, mentor_data_root: str, mentor_id: str
):
    _test_utterances_update_transcripts(
        mock_init_transcription_service, mentor_data_root, mentor_id, test_logging=True
    )


def _test_utterances_update_transcripts(
    mock_init_transcription_service,
    mentor_data_root: str,
    mentor_id: str,
    test_logging=False,
    force_update=False,
):
    with patch("logging.info") as mock_logging_info:
        mpath = copy_mentor_to_tmp(mentor_id, mentor_data_root)
        input_utterances = mpath.load_utterances()
        mock_transcriptions = MockTranscriptions(
            mpath,
            mock_init_transcription_service,
            mock_logging_info=mock_logging_info if test_logging else None,
        )
        dummy_transcription_service = mock_init_transcription_service()
        expected_utterances = utterances_from_yaml(
            mpath.get_mentor_data("expected-utterances.yaml")
        )
        mock_transcriptions.mock_transcribe_result_and_callbacks()
        actual_utterances = update_transcripts(
            input_utterances,
            dummy_transcription_service,
            mpath,
            on_update=mock_transcriptions.mock_on_update(),
            force_update=force_update,
        )
        mock_transcriptions.expect_calls()
        assert expected_utterances.to_dict() == actual_utterances.to_dict()
