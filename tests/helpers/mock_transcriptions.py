from typing import Callable
from unittest.mock import Mock

from mentor_pipeline.mentorpath import MentorPath
from transcribe import TranscribeJobsUpdate
from transcribe.mock import mock_transcribe_call_fixture_from_yaml, MockTranscriptions as _MockTranscriptions
from mentor_pipeline.utterance_asset_type import UTTERANCE_AUDIO


class MockTranscriptions:
    """
    Test-helper class for mocking the TranscriptionService
    (which is presumably an online API).

    To use, create a mock-transcribe-call.yaml file in the root
    of a test-mentor directory and fill with entries like this:

        - audio: build/utterance_audio/s001p001s00000000e00000100.mp3
          transcript: mentor answer to question 1

    then call `load_expected_calls` to set up the mock
    to expect the calls and return the transcripts as configured
    """

    def __init__(
        self,
        mpath: MentorPath,
        mock_init_transcription_service: Mock,
        mock_logging_info: Mock = None,
    ):
        self.mpath = mpath
        self.mock_transcriptions = _MockTranscriptions(mock_init_transcription_service, mpath.get_mentor_asset(
            UTTERANCE_AUDIO.get_mentor_asset_root()
        ))
        # self.mock_service = Mock()
        # self.mock_logging_info = mock_logging_info
        self.source_file_root_path = mpath.get_mentor_asset(
            UTTERANCE_AUDIO.get_mentor_asset_root()
        )
        # mock_init_transcription_service.return_value = self.mock_service

    def expect_calls(self) -> None:
        self.mock_transcriptions.expect_on_update_called_once_per_fixture_update()

    def mock_on_update(self) -> Callable[[TranscribeJobsUpdate], None]:
        i = 0

        _base_on_update = self.mock_transcriptions.mock_on_update()

        def _on_update(update: TranscribeJobsUpdate) -> None:
            _base_on_update(update)
            utterances = self.mpath.load_utterances()
            for j in update.result.jobs():
                u = utterances.find_by_id(j.jobId)
                assert u.transcript == j.transcript, f"update [{i}] expected utterance {u.get_id()} to have transcript '{j.transcript}' but was '{u.transcript}'"

        return _on_update

    def mock_transcribe_result_and_callbacks(
        self,
        mock_transcribe_call_yaml="mock-transcribe-call.yaml",
    ) -> None:
        fixture = mock_transcribe_call_fixture_from_yaml(self.mpath.get_mentor_data(mock_transcribe_call_yaml))
        self.mock_transcriptions.mock_transcribe_result_and_callbacks(fixture)
