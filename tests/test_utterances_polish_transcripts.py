import pytest

from .helpers import (
    assert_utterances_match_expected,
    copy_mentor_to_tmp,
    resource_root_mentors_for_test,
)
from mentor_pipeline.process import polish_transcripts

MENTOR_DATA_ROOT = resource_root_mentors_for_test(__file__)


@pytest.mark.parametrize("mentor_root,mentor_id", [(MENTOR_DATA_ROOT, "mentor1")])
def test_it_capitilizes_transcript_sentences(mentor_root: str, mentor_id: str):
    _test_polish_utterances(mentor_root, mentor_id)


def _test_polish_utterances(mentor_data_root: str, mentor_id: str):
    mpath = copy_mentor_to_tmp(mentor_id, mentor_data_root)
    input_utterances = mpath.load_utterances()
    actual_utterances = polish_transcripts(input_utterances, mpath)
    assert_utterances_match_expected(mpath, actual_utterances)
