#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
import os
import pytest

from .helpers import (
    assert_utterance_asset_exists,
    copy_mentor_to_tmp,
    resource_root_mentors_for_test,
)
from mentor_pipeline.process import utterances_to_captions
from mentor_pipeline.utterance_asset_type import UTTERANCE_CAPTIONS

MENTOR_DATA_ROOT = resource_root_mentors_for_test(__file__)


@pytest.mark.parametrize("mentor_root,mentor_id", [(MENTOR_DATA_ROOT, "mentor1")])
def test_it_generates_captions_for_utterances(mentor_root: str, mentor_id: str):
    _test_it_generates_captions_for_utterances(mentor_root, mentor_id)


def _test_it_generates_captions_for_utterances(mentor_root: str, mentor_id: str):
    mp = copy_mentor_to_tmp(mentor_id, mentor_root)
    utterances = mp.load_utterances()
    captions_by_utterance_id = utterances_to_captions(
        utterances, mp
    ).captions_by_utterance_id
    for uid, actual_captions in captions_by_utterance_id.items():
        expected_captions_path = mp.get_mentor_data(
            os.path.join("expected_captions", f"{uid}.vtt")
        )
        with open(expected_captions_path, "r") as f_expected:
            expected_captions = f_expected.read()
            assert expected_captions == actual_captions
            u = utterances.find_by_id(uid)
            assert_utterance_asset_exists(mp, u, UTTERANCE_CAPTIONS)
            actual_captions_path = mp.find_utterance_captions(u)
            with open(actual_captions_path, "r") as f_actual:
                assert expected_captions == f_actual.read()
