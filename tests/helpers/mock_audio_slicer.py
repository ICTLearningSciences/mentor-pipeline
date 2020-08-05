# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
import os
from unittest.mock import call, Mock

from mentor_pipeline.mentorpath import MentorPath
from mentor_pipeline.utils import yaml_load


class MockAudioSlicer:
    """
    Mocks `media_tools.slice_audio` to create dummy versions
    of the audio files that would be output by the real function.

    This helps test cases that go through code that transcribes the audio.
    The transcriptions can be easily mocked to return fake transcriptions,
    but the code will generally check the existance of the files first
    and fail if it doesn't find them.
    """

    def _on_slice_audio_create_dummy_output(  # noqa: E302
        self, src_file: str, target_file: str, time_start: float, time_end: float
    ) -> None:
        output_command = (
            f"-ss {time_start} -to {time_end} -c:a libvorbis -q:a 5 -loglevel quiet"
        )
        os.makedirs(os.path.dirname(target_file), exist_ok=True)
        with open(target_file, "w") as f:
            f.write(
                f"ffmpy.FFmpeg(inputs={{{src_file}: None}} outputs={{{target_file}: {output_command}}}"
            )

    def __init__(
        self,
        mock_slice_audio: Mock,
        mock_logging_info: Mock = None,
        create_dummy_output_files=True,
    ):
        self.mock_slice_audio = mock_slice_audio
        self.mock_logging_info = mock_logging_info
        self.create_dummy_output_files = create_dummy_output_files
        if create_dummy_output_files:
            mock_slice_audio.side_effect = self._on_slice_audio_create_dummy_output

    def assert_has_calls(
        self,
        mpath: MentorPath,
        expected_calls_yaml="expected-slice-audio-calls.yaml",
        fail_on_no_calls=False,
    ) -> None:
        expected_calls_yaml_path = mpath.get_mentor_data(expected_calls_yaml)
        if fail_on_no_calls:
            assert os.path.isfile(
                expected_calls_yaml_path
            ), f"expected mock-slice-audio calls at path {expected_calls_yaml_path}"
        expected_calls_data = yaml_load(expected_calls_yaml_path)
        expected_calls = [
            call(
                mpath.get_mentor_data(call_data.get("source")),
                mpath.get_mentor_data(call_data.get("target")),
                call_data.get("time_start_secs"),
                call_data.get("time_end_secs"),
            )
            for call_data in expected_calls_data
        ]
        expected_calls_logging_info = [
            call(
                f"utterance_to_audio [{i + 1}/{len(expected_calls_data)}] source={mpath.get_mentor_data(call_data.get('source'))}, target={mpath.get_mentor_data(call_data.get('target'))}, time-start={call_data.get('time_start_secs')}, time-end={call_data.get('time_end_secs')}"
            )
            for i, call_data in enumerate(expected_calls_data)
        ]
        if fail_on_no_calls:
            assert (
                len(expected_calls) > 0
            ), f"expected mock-slice-audio calls at path {expected_calls_yaml_path}"
        self.mock_slice_audio.assert_has_calls(expected_calls)
        if self.mock_logging_info:
            self.mock_logging_info.assert_has_calls(expected_calls_logging_info)
