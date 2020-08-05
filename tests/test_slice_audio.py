# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
import os
from unittest.mock import patch

import pytest

from .helpers import resource_root_mentors_for_test
from mentor_pipeline.mentorpath import MentorPath
from mentor_pipeline.media_tools import slice_audio


MENTOR_DATA_ROOT = resource_root_mentors_for_test(__file__)


@patch("os.makedirs")
@patch("ffmpy.FFmpeg")
@pytest.mark.parametrize("mentor_data_root,mentor_id", [(MENTOR_DATA_ROOT, "mentor1")])
def test_it_creates_directories_for_output_as_needed(
    mock_ffmpeg, mock_make_dirs, mentor_data_root: str, mentor_id: str
):
    mpath = MentorPath(mentor_id=mentor_id, root_path_data_mentors=mentor_data_root)
    audio_src = mpath.get_mentor_data(
        os.path.join("build", "recordings", "session1", "p1-some-questions.mp3")
    )
    audio_tgt = os.path.join("build", "utterance_audio", "utterance1.mp3")
    slice_audio(audio_src, audio_tgt, 0.0, 1.0)
    mock_make_dirs.assert_called_once_with(os.path.dirname(audio_tgt), exist_ok=True)
