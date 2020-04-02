import os
from unittest.mock import call, Mock

from mentor_pipeline.mentorpath import MentorPath
from mentor_pipeline.utils import yaml_load


class MockNoiseReducer:
    """
    Spy `noise._reduce_noise`
    """

    def __init__(self, mock_reduce_noise: Mock):
        self.mock_reduce_noise = mock_reduce_noise

    def assert_has_calls(
        self,
        mpath: MentorPath,
        expected_calls_yaml="expected-reduce-noise-calls.yaml",
        fail_on_no_calls=False,
    ) -> None:
        expected_calls_yaml_path = mpath.get_mentor_data(expected_calls_yaml)
        if fail_on_no_calls:
            assert os.path.isfile(
                expected_calls_yaml_path
            ), f"expected mock-reduce-noise calls at path {expected_calls_yaml_path}"
        expected_calls_data = yaml_load(expected_calls_yaml_path)
        expected_calls = [
            call(
                mpath.get_mentor_data(call_data.get("noise_sample")),
                mpath.get_mentor_video(call_data.get("target")),
            )
            for call_data in expected_calls_data
        ]
        if fail_on_no_calls:
            assert (
                len(expected_calls) > 0
            ), f"expected mock-reduce-noise  calls at path {expected_calls_yaml_path}"
        self.mock_reduce_noise.assert_has_calls(expected_calls)
