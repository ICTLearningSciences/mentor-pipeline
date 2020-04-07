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
