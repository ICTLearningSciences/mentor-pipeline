#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
import os
import pytest
from unittest.mock import patch

from .helpers import (
    assert_utterances_match_expected,
    copy_mentor_to_tmp,
    MockVideoSlicer,
    resource_root_mentors_for_test,
)
from mentor_pipeline.process import utterances_slice_video


MENTOR_ROOT = resource_root_mentors_for_test(__file__)


@pytest.mark.parametrize("mentor_root,mentor_id", [(MENTOR_ROOT, "mentor1")])
def test_it_generates_a_video_file_for_each_utterance(mentor_root: str, mentor_id: str):
    _test_utterance_to_video(mentor_root, mentor_id, require_video_to_audio_calls=False)


@pytest.mark.parametrize(
    "mentor_root,mentor_id", [(MENTOR_ROOT, "mentor2-skips-existing-video")]
)
def test_it_skips_utterances_with_existing_video_and_unchanged_start_and_end_times(
    mentor_root: str, mentor_id: str
):
    _test_utterance_to_video(mentor_root, mentor_id, require_video_to_audio_calls=False)


@pytest.mark.parametrize(
    "mentor_root,mentor_id", [(MENTOR_ROOT, "mentor3-encodes-missing-video")]
)
def test_it_encodes_missing_video(mentor_root: str, mentor_id: str):
    _test_utterance_to_video(mentor_root, mentor_id, require_video_to_audio_calls=False)


@pytest.mark.parametrize(
    "mentor_root,mentor_id", [(MENTOR_ROOT, "mentor2-skips-existing-video")]
)
def test_it_logs_info_for_each_call_to_generate_utterance_video(
    mentor_root: str, mentor_id: str
):
    _test_utterance_to_video(
        mentor_root, mentor_id, require_video_to_audio_calls=False, test_logging=True
    )


def _test_utterance_to_video(
    mentor_root: str,
    mentor_id: str,
    require_video_to_audio_calls: bool = True,
    require_video_slice_calls: bool = True,
    test_logging=False,
):
    with patch("mentor_pipeline.media_tools.slice_video") as mock_slice_video, patch(
        "logging.info"
    ) as mock_logging_info:
        mp = copy_mentor_to_tmp(
            mentor_id, os.path.join(mentor_root, mentor_id, "data", "mentors")
        )
        mock_video_slicer = MockVideoSlicer(
            mock_slice_video,
            mock_logging_info=mock_logging_info if test_logging else None,
        )
        utterances_before = mp.load_utterances()
        actual_utterances = utterances_slice_video(utterances_before, mp)
        mock_video_slicer.assert_has_calls(
            mp, fail_on_no_calls=require_video_slice_calls
        )
        assert_utterances_match_expected(mp, utterances=actual_utterances)
