import os
from unittest.mock import call, Mock

from mentor_pipeline.mentorpath import MentorPath
from mentor_pipeline.utils import yaml_load


class MockVideoSlicer:
    """
    Mocks `media_tools.slice_video` to create dummy versions
    of the video files that would be output by the real function.
    """

    def _on_slice_create_dummy_output(
        self, src_file: str, tgt_file: str, time_start: float, time_end: float
    ) -> None:
        os.makedirs(os.path.dirname(tgt_file), exist_ok=True)
        with open(tgt_file, "w") as f:
            f.write(
                f"ffmpy.FFmpeg(inputs={{{src_file}: None}} outputs={{{tgt_file}: some command}} --ss {time_start} --to {time_end}"
            )

    def __init__(
        self,
        mock_slice_video: Mock,
        mock_logging_info: Mock = None,
        create_dummy_output_files=True,
    ):
        self.mock_slice_video = mock_slice_video
        self.mock_logging_info = mock_logging_info
        self.create_dummy_output_files = create_dummy_output_files
        if create_dummy_output_files:
            mock_slice_video.side_effect = self._on_slice_create_dummy_output

    def assert_has_calls(
        self,
        mpath: MentorPath,
        expected_calls_yaml="expected-slice-video-calls.yaml",
        fail_on_no_calls=False,
    ) -> None:
        expected_calls_yaml_path = mpath.get_mentor_data(expected_calls_yaml)
        if fail_on_no_calls:
            assert os.path.isfile(
                expected_calls_yaml_path
            ), f"expected mock-slice-video calls at path {expected_calls_yaml_path}"
        expected_calls_data = yaml_load(expected_calls_yaml_path)
        expected_calls = [
            call(
                mpath.get_mentor_data(call_data.get("source")),
                mpath.get_mentor_video(call_data.get("target")),
                call_data.get("time_start_secs"),
                call_data.get("time_end_secs"),
            )
            for call_data in expected_calls_data
        ]
        expected_calls_logging_info = [
            call(
                f"utterance_to_video [{i + 1}/{len(expected_calls_data)}] source={mpath.get_mentor_data(call_data.get('source'))}, target={mpath.get_mentor_video(call_data.get('target'))}, time-start={call_data.get('time_start_secs')}, time-end={call_data.get('time_end_secs')}"
            )
            for i, call_data in enumerate(expected_calls_data)
        ]
        if fail_on_no_calls:
            assert (
                len(expected_calls) > 0
            ), f"expected mock-slice-video calls at path {expected_calls_yaml_path}"
        self.mock_slice_video.assert_has_calls(expected_calls)
        if self.mock_logging_info:
            self.mock_logging_info.assert_has_calls(expected_calls_logging_info)
