# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
import os

import pytest
from unittest.mock import patch

from .helpers import (
    MockNoiseReducer,
    copy_mentor_to_tmp,
    resource_root_mentors_for_test,
)
from mentor_pipeline.run import Pipeline

MENTOR_ROOT = resource_root_mentors_for_test(__file__)


@patch("mentor_pipeline.noise.reduce_noise")
@pytest.mark.parametrize("mentor_root,mentor_id", [(MENTOR_ROOT, "mentor1")])
def test_run_videos_reduce_noise_applies_noise_reduction(
    mock_noise_reducer, mentor_root: str, mentor_id: str
):
    mpath = copy_mentor_to_tmp(
        mentor_id, os.path.join(mentor_root, mentor_id, "data", "mentors")
    )
    mock_noise_reducer = MockNoiseReducer(mock_noise_reducer)
    p = Pipeline(mentor_id, mpath.root_path_data_mentors)
    p.videos_reduce_noise()
    mock_noise_reducer.assert_has_calls(mpath)
