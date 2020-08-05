# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
import pytest

from .helpers import assert_utterances_match_expected, resource_root_mentors_for_test
from mentor_pipeline.mentorpath import MentorPath
from mentor_pipeline.process import sync_timestamps


MENTOR_DATA_ROOT = resource_root_mentors_for_test(__file__)


@pytest.mark.parametrize(
    "mentor_data_root,mentor_id", [(MENTOR_DATA_ROOT, "mentor1-clean-slate")]
)
def test_it_generates_utterances_from_timestamps(mentor_data_root: str, mentor_id: str):
    _test_synced_utterances_match_expected(mentor_data_root, mentor_id)


@pytest.mark.parametrize(
    "mentor_data_root,mentor_id",
    [(MENTOR_DATA_ROOT, "mentor2-preserves-transcripts-when-merging")],
)
def test_it_preserves_transcripts_when_merging(mentor_data_root: str, mentor_id: str):
    _test_synced_utterances_match_expected(mentor_data_root, mentor_id)


@pytest.mark.parametrize(
    "mentor_data_root,mentor_id", [(MENTOR_DATA_ROOT, "mentor3-fixes-smart-quotes")]
)
def test_it_fixes_smart_quotes(mentor_data_root: str, mentor_id: str):
    _test_synced_utterances_match_expected(mentor_data_root, mentor_id)


@pytest.mark.parametrize(
    "mentor_data_root,mentor_id", [(MENTOR_DATA_ROOT, "mentor4-assigns-asset-paths")]
)
def test_it_assigns_asset_paths(mentor_data_root: str, mentor_id: str):
    _test_synced_utterances_match_expected(mentor_data_root, mentor_id)


@pytest.mark.parametrize(
    "mentor_data_root,mentor_id",
    [(MENTOR_DATA_ROOT, "mentor5-works-with-period-delimited-timestamp-formats")],
)
def test_it_works_with_period_delimited_timestamp_formats(
    mentor_data_root: str, mentor_id: str
):
    _test_synced_utterances_match_expected(mentor_data_root, mentor_id)


def _test_synced_utterances_match_expected(mentor_data_root: str, mentor_id: str):
    mp = MentorPath(mentor_id=mentor_id, root_path_data_mentors=mentor_data_root)
    actual_utterances = sync_timestamps(mp)
    assert_utterances_match_expected(mp, utterances=actual_utterances)
