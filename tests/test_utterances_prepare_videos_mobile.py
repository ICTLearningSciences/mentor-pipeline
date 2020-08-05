# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
import os
import pytest
from unittest.mock import patch

from .helpers import (
    assert_utterances_match_expected,
    copy_mentor_to_tmp,
    MockMediaConverter,
    resource_root_mentors_for_test,
)
from mentor_pipeline.process import prepare_videos_mobile


MENTOR_ROOT = resource_root_mentors_for_test(__file__)


@pytest.mark.parametrize("mentor_root,mentor_id", [(MENTOR_ROOT, "mentor1")])
def test_it_prepares_a_mobile_video_for_each_utterance(
    mentor_root: str, mentor_id: str
):
    _test_utterances_prepare_videos_mobile(mentor_root, mentor_id)


@pytest.mark.parametrize(
    "mentor_root,mentor_id", [(MENTOR_ROOT, "mentor2-skips-existing-video")]
)
def test_it_skips_utterances_with_existing_mobile_video(
    mentor_root: str, mentor_id: str
):
    _test_utterances_prepare_videos_mobile(mentor_root, mentor_id)


@pytest.mark.parametrize(
    "mentor_root,mentor_id", [(MENTOR_ROOT, "mentor2-skips-existing-video")]
)
def test_it_logs_info_for_each_call_to_generate_mobile_video(
    mentor_root: str, mentor_id: str
):
    _test_utterances_prepare_videos_mobile(mentor_root, mentor_id, test_logging=True)


def _test_utterances_prepare_videos_mobile(
    mentor_root: str, mentor_id: str, test_logging=False
):
    with patch(
        "mentor_pipeline.media_tools.video_encode_for_mobile"
    ) as mock_video_encode, patch("logging.info") as mock_logging_info:
        mp = copy_mentor_to_tmp(
            mentor_id, os.path.join(mentor_root, mentor_id, "data", "mentors")
        )
        mock_media_converter = MockMediaConverter(
            mock_video_encode,
            mock_logging_info=mock_logging_info if test_logging else None,
        )
        utterances_before = mp.load_utterances()
        actual_utterances = prepare_videos_mobile(utterances_before, mp)
        mock_media_converter.expect_calls(
            mp, logging_function_name="prepare_videos_mobile"
        )
        assert_utterances_match_expected(mp, utterances=actual_utterances)
