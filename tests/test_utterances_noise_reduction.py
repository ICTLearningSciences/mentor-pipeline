import os
import pytest
from unittest.mock import patch

from .helpers import (
    copy_mentor_to_tmp,
    MockNoiseReducer,
    resource_root_mentors_for_test,
)
from mentor_pipeline.process import utterances_noise_reduction


MENTOR_ROOT = resource_root_mentors_for_test(__file__)


@pytest.mark.parametrize(
    "mentor_root,mentor_id",
    [(MENTOR_ROOT, "mentor1-matches-noise-sample-to-utterance_by_prefix")],
)
def test_it_matches_noise_sample_to_utterance_by_prefix(
    mentor_root: str, mentor_id: str
):
    _test_utterance_noise_reduction(mentor_root, mentor_id)


def _test_utterance_noise_reduction(
    mentor_root: str, mentor_id: str, require_reduce_noise_calls: bool = True
):
    with patch("mentor_pipeline.noise.reduce_noise") as mock_reduce_noise:
        mp = copy_mentor_to_tmp(
            mentor_id, os.path.join(mentor_root, mentor_id, "data", "mentors")
        )
        mock_noise_reducer = MockNoiseReducer(mock_reduce_noise)
        utterances = mp.load_utterances()
        utterances_noise_reduction(utterances, mp)
        mock_noise_reducer.assert_has_calls(
            mp, fail_on_no_calls=require_reduce_noise_calls
        )
