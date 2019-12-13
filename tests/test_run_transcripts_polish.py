import os

import pandas as pd
import pytest

from .helpers import (
    assert_captions_match_expected,
    assert_utterances_match_expected,
    copy_mentor_to_tmp,
    resource_root_mentors_for_test,
)
from mentor_pipeline.run import Pipeline
from mentor_pipeline.training_data import (
    load_classifier_data,
    load_utterance_data,
)

MENTOR_DATA_ROOT = resource_root_mentors_for_test(__file__)


@pytest.mark.parametrize(
    "mentor_data_root,mentor_id",
    [(MENTOR_DATA_ROOT, "mentor1")],
)
def test_it_polishes_transcripts(
    mentor_data_root: str,
    mentor_id: str,
):
    mpath = copy_mentor_to_tmp(mentor_id, mentor_data_root)
    p = Pipeline(mentor_id, mpath.root_path_data_mentors)
    p.transcripts_polish()
    assert_utterances_match_expected(mpath)
    expected_utterance_data = load_utterance_data(
        mpath.get_mentor_data(os.path.join("expected_data"))
    )
    actual_utterance_data = mpath.load_training_utterance_data()
    pd.testing.assert_frame_equal(expected_utterance_data, actual_utterance_data)
    expected_classifier_data = load_classifier_data(
        mpath.get_mentor_data(os.path.join("expected_data"))
    )
    actual_classifier_data = mpath.load_training_classifier_data()
    pd.testing.assert_frame_equal(expected_classifier_data, actual_classifier_data)
    assert_captions_match_expected(mpath)
