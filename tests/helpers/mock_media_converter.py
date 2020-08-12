#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
import os
from unittest.mock import call, Mock

from mentor_pipeline.mentorpath import MentorPath
from mentor_pipeline.utils import yaml_load


class MockMediaConverter:
    """
    Mocks a function that converts media having args src and tgt.
    Can also create dummy files at the target paths

    This helps test cases that go through code that needs session audio
    """

    def _on_convert_create_dummy_output(self, src_file: str, tgt_file: str) -> None:
        os.makedirs(os.path.dirname(tgt_file), exist_ok=True)
        with open(tgt_file, "w") as f:
            f.write(
                f"ffmpy.FFmpeg(inputs={{{src_file}: None}} outputs={{{tgt_file}: some command}}"
            )

    def __init__(
        self,
        mock_convert_src_to_tgt: Mock,
        mock_logging_info: Mock = None,
        create_dummy_output_files=True,
    ):
        self.mock_convert_src_to_tgt = mock_convert_src_to_tgt
        self.mock_logging_info = mock_logging_info
        self.create_dummy_output_files = create_dummy_output_files
        if create_dummy_output_files:
            mock_convert_src_to_tgt.side_effect = self._on_convert_create_dummy_output

    def expect_calls(
        self,
        mpath: MentorPath,
        expected_calls_yaml="expected-media-converter-calls.yaml",
        logging_function_name="media_converter",
        fail_on_no_calls=False,
    ) -> None:
        yaml_path = mpath.get_mentor_data(expected_calls_yaml)
        if not os.path.isfile(yaml_path):
            if fail_on_no_calls:
                raise (Exception(f"expected calls yaml file at path {yaml_path}"))
            else:
                return
        mock_calls = yaml_load(yaml_path)
        expected_calls = []
        expected_calls_logging_info = []
        for i, call_data in enumerate(mock_calls):
            src_path = mpath.get_mentor_video(call_data.get("source"))
            tgt_path = mpath.get_mentor_video(call_data.get("target"))
            expected_calls.append(call(src_path, tgt_path))
            expected_calls_logging_info.append(
                call(
                    f"{logging_function_name} [{i + 1}/{len(mock_calls)}] source={src_path}, target={tgt_path}"
                )
            )
        if fail_on_no_calls and not expected_calls:
            raise (Exception(f"expected mock-media-converter calls"))
        self.mock_convert_src_to_tgt.assert_has_calls(expected_calls)
        if self.mock_logging_info:
            self.mock_logging_info.assert_has_calls(expected_calls_logging_info)
