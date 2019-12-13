from typing import Callable
import logging

from unittest.mock import call, Mock

from mentor_pipeline.mentorpath import MentorPath
from mentor_pipeline.utils import yaml_load
from mentor_pipeline.process import OnDidTranscribe
from mentor_pipeline.utterances import Utterance


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
        self.mock_service = Mock()
        self.mock_logging_info = mock_logging_info
        mock_init_transcription_service.return_value = self.mock_service

    def expect_calls(self) -> None:
        self.mock_service.transcribe.assert_has_calls(self.expected_transcribe_calls)
        if self.mock_logging_info:
            self.mock_logging_info.assert_has_calls(self.expected_calls_logging_info)

    def get_on_did_transcribe(self) -> Callable[[OnDidTranscribe], None]:
        # Test after each on_did_transcribe callback
        # that the latest transcription was written.
        # This is important in case a large batch of transcriptions
        # only completes partially.
        # We don't want to lose the completed transcriptions
        def on_did_transcribe(cb: OnDidTranscribe):
            logging.warning(f"on_did_transcribe {cb} called!\n\n\n")
            utterances = self.mpath.load_utterances()
            assert cb.utterance_id is not None
            u = utterances.find_by_id(cb.utterance_id)
            assert isinstance(u, Utterance)
            assert u.transcript == cb.transcript
            assert u.transcript in self.expectected_transcriptions

        return on_did_transcribe

    def load_expected_calls(
        self, mock_transcribe_calls_yaml="mock-transcribe-calls.yaml"
    ) -> None:
        mock_transcribe_calls = yaml_load(
            self.mpath.get_mentor_data(mock_transcribe_calls_yaml)
        )
        self.expected_transcribe_calls = []
        self.expected_calls_logging_info = []
        self.expectected_transcriptions = []
        expected_transcribe_returns = []
        for i, call_data in enumerate(mock_transcribe_calls):
            audio_path = self.mpath.get_mentor_data(call_data.get("audio"))
            transcript = call_data.get("transcript")
            self.expected_transcribe_calls.append(call(audio_path))
            self.expectected_transcriptions.append(transcript)
            expected_transcribe_returns.append(transcript)
            self.expected_calls_logging_info.append(
                call(
                    f"transcribe [{i + 1}/{len(mock_transcribe_calls)}] audio={audio_path}"
                )
            )
        self.mock_service.transcribe.side_effect = expected_transcribe_returns
