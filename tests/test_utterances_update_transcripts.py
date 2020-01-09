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
@pytest.mark.parametrize("mentor_data_root,mentor_id", [(MENTOR_DATA_ROOT, "mentor2-writes-on-update")])
def test_it_writes_transcriptions_to_utterances_on_each_update_callback(
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
        )
        mock_transcriptions.expect_calls()
        assert expected_utterances.to_dict() == actual_utterances.to_dict()
