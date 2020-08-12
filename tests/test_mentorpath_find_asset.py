#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
import os
from typing import List

import pytest
from unittest.mock import patch

from .helpers import mock_isfile_with_paths
from mentor_pipeline.utterance_asset_type import (
    UtteranceAssetType,
    SESSION_AUDIO,
    SESSION_TIMESTAMPS,
    SESSION_VIDEO,
    UTTERANCE_AUDIO,
    UTTERANCE_VIDEO,
)
from mentor_pipeline.mentorpath import MentorPath
from mentor_pipeline.utterances import Utterance


@patch("os.path.isfile")
@pytest.mark.parametrize(
    "utterance_dict,asset_type,expected_rel_path",
    [
        (
            dict(sessionAudio="build/recordings/session1/p001-some-questions.mp3"),
            SESSION_AUDIO,
            "build/recordings/session1/p001-some-questions.mp3",
        ),
        (
            dict(sessionTimestamps="build/recordings/session1/p001-some-questions.csv"),
            SESSION_TIMESTAMPS,
            "build/recordings/session1/p001-some-questions.csv",
        ),
        (
            dict(sessionVideo="build/recordings/session1/p001-some-questions.mp4"),
            SESSION_VIDEO,
            "build/recordings/session1/p001-some-questions.mp4",
        ),
        (
            dict(utteranceAudio="build/utterance_audio/s001p001s00000000e00000000.mp3"),
            UTTERANCE_AUDIO,
            "build/utterance_audio/s001p001s00000000e00000000.mp3",
        ),
        (
            dict(utteranceVideo="build/utterance_video/s001p001s00000000e00000000.mp4"),
            UTTERANCE_VIDEO,
            "build/utterance_video/s001p001s00000000e00000000.mp4",
        ),
    ],
)
def test_it_finds_existing_assets_that_have_path_set(
    mock_isfile,
    utterance_dict: dict,
    asset_type: UtteranceAssetType,
    expected_rel_path: str,
):
    _test_it_finds(
        mock_isfile, utterance_dict, asset_type, [expected_rel_path], expected_rel_path
    )


@patch("os.path.isfile")
@pytest.mark.parametrize(
    "utterance_dict,asset_type,expected_rel_path",
    [
        (
            dict(sessionTimestamps="build/recordings/session1/p001-some-questions.csv"),
            SESSION_AUDIO,
            "build/recordings/session1/p001-some-questions.mp3",
        ),
        (
            dict(sessionVideo="build/recordings/session1/p001-some-questions.mp4"),
            SESSION_AUDIO,
            "build/recordings/session1/p001-some-questions.mp3",
        ),
        (
            dict(sessionVideo="build/recordings/session1/p001-some-questions.mp4"),
            SESSION_TIMESTAMPS,
            "build/recordings/session1/p001-some-questions.csv",
        ),
        (
            dict(sessionAudio="build/recordings/session1/p001-some-questions.mp3"),
            SESSION_TIMESTAMPS,
            "build/recordings/session1/p001-some-questions.csv",
        ),
        (
            dict(sessionAudio="build/recordings/session1/p001-some-questions.mp3"),
            SESSION_VIDEO,
            "build/recordings/session1/p001-some-questions.mp4",
        ),
        (
            dict(sessionTimestamps="build/recordings/session1/p001-some-questions.mp3"),
            SESSION_VIDEO,
            "build/recordings/session1/p001-some-questions.mp4",
        ),
        (
            dict(utteranceVideo="build/utterance_video/s001p001s00000000e00000000.mp4"),
            UTTERANCE_AUDIO,
            "build/utterance_audio/s001p001s00000000e00000000.mp3",
        ),
        (
            dict(utteranceAudio="build/utterance_audio/s001p001s00000000e00000000.mp3"),
            UTTERANCE_VIDEO,
            "build/utterance_video/s001p001s00000000e00000000.mp4",
        ),
    ],
)
def test_it_finds_existing_assets_that_whose_path_can_be_inferred(
    mock_isfile,
    utterance_dict: dict,
    asset_type: UtteranceAssetType,
    expected_rel_path: str,
):
    _test_it_finds(
        mock_isfile, utterance_dict, asset_type, [expected_rel_path], expected_rel_path
    )


@patch("os.path.isfile")
@pytest.mark.parametrize(
    "utterance_dict,asset_type,expected_rel_path",
    [
        (
            dict(sessionTimestamps="build/recordings/session1/p001-some-questions.csv"),
            SESSION_AUDIO,
            "",
        ),
        (
            dict(sessionVideo="build/recordings/session1/p001-some-questions.mp4"),
            SESSION_AUDIO,
            "",
        ),
        (
            dict(sessionVideo="build/recordings/session1/p001-some-questions.mp4"),
            SESSION_TIMESTAMPS,
            "",
        ),
        (
            dict(sessionAudio="build/recordings/session1/p001-some-questions.mp3"),
            SESSION_TIMESTAMPS,
            "",
        ),
        (
            dict(sessionAudio="build/recordings/session1/p001-some-questions.mp3"),
            SESSION_VIDEO,
            "",
        ),
        (
            dict(sessionTimestamps="build/recordings/session1/p001-some-questions.mp3"),
            SESSION_VIDEO,
            "",
        ),
    ],
)
def test_it_returns_none_by_default_if_path_does_not_exist(
    mock_isfile,
    utterance_dict: dict,
    asset_type: UtteranceAssetType,
    expected_rel_path: str,
):
    _test_it_finds(mock_isfile, utterance_dict, asset_type, [], expected_rel_path)


@patch("os.path.isfile")
@pytest.mark.parametrize(
    "utterance_dict,asset_type,expected_rel_path",
    [
        (
            dict(sessionAudio="build/recordings/session1/p001-some-questions.mp3"),
            SESSION_AUDIO,
            "build/recordings/session1/p001-some-questions.mp3",
        ),
        (
            dict(sessionTimestamps="build/recordings/session1/p001-some-questions.csv"),
            SESSION_TIMESTAMPS,
            "build/recordings/session1/p001-some-questions.csv",
        ),
        (
            dict(sessionVideo="build/recordings/session1/p001-some-questions.mp4"),
            SESSION_VIDEO,
            "build/recordings/session1/p001-some-questions.mp4",
        ),
        (
            dict(utteranceAudio="build/utterance_audio/s001p001s00000000e00000000.mp3"),
            UTTERANCE_AUDIO,
            "build/utterance_audio/s001p001s00000000e00000000.mp3",
        ),
        (
            dict(utteranceVideo="build/utterance_video/s001p001s00000000e00000000.mp4"),
            UTTERANCE_VIDEO,
            "build/utterance_video/s001p001s00000000e00000000.mp4",
        ),
        (
            dict(sessionTimestamps="build/recordings/session1/p001-some-questions.csv"),
            SESSION_AUDIO,
            "build/recordings/session1/p001-some-questions.mp3",
        ),
        (
            dict(sessionVideo="build/recordings/session1/p001-some-questions.mp4"),
            SESSION_AUDIO,
            "build/recordings/session1/p001-some-questions.mp3",
        ),
        (
            dict(sessionVideo="build/recordings/session1/p001-some-questions.mp4"),
            SESSION_TIMESTAMPS,
            "build/recordings/session1/p001-some-questions.csv",
        ),
        (
            dict(sessionAudio="build/recordings/session1/p001-some-questions.mp3"),
            SESSION_TIMESTAMPS,
            "build/recordings/session1/p001-some-questions.csv",
        ),
        (
            dict(sessionAudio="build/recordings/session1/p001-some-questions.mp3"),
            SESSION_VIDEO,
            "build/recordings/session1/p001-some-questions.mp4",
        ),
        (
            dict(sessionTimestamps="build/recordings/session1/p001-some-questions.mp3"),
            SESSION_VIDEO,
            "build/recordings/session1/p001-some-questions.mp4",
        ),
        (
            dict(utteranceVideo="build/utterance_video/s001p001s00000000e00000000.mp4"),
            UTTERANCE_AUDIO,
            "build/utterance_audio/s001p001s00000000e00000000.mp3",
        ),
        (
            dict(utteranceAudio="build/utterance_audio/s001p001s00000000e00000000.mp3"),
            UTTERANCE_VIDEO,
            "build/utterance_video/s001p001s00000000e00000000.mp4",
        ),
    ],
)
def test_it_returns_path_that_does_not_exist_on_request(
    mock_isfile,
    utterance_dict: dict,
    asset_type: UtteranceAssetType,
    expected_rel_path: str,
):
    _test_it_finds(
        mock_isfile,
        utterance_dict,
        asset_type,
        [],
        expected_rel_path,
        return_non_existing_paths=True,
    )


@patch("os.path.isfile")
@pytest.mark.parametrize(
    "utterance_dict,asset_type,expected_rel_path",
    [
        (
            dict(session=1, part=2, timeStart=2.34, timeEnd=3.45),
            UTTERANCE_AUDIO,
            "build/utterance_audio/s001p002s00000234e00000345.mp3",
        )
    ],
)
def test_it_constructs_default_paths_when_no_path_configured(
    mock_isfile,
    utterance_dict: dict,
    asset_type: UtteranceAssetType,
    expected_rel_path: str,
):
    _test_it_finds(
        mock_isfile,
        utterance_dict,
        asset_type,
        [],
        expected_rel_path,
        return_non_existing_paths=True,
    )


def _test_it_finds(
    mock_isfile,
    utterance_dict: dict,
    asset_type: UtteranceAssetType,
    existing_files: List[str],
    expected_rel_path: str,
    return_non_existing_paths=False,
):
    mentor_id = "m1"
    mentor_root = os.path.abspath(os.path.curdir)
    mpath = MentorPath(
        mentor_id=mentor_id,
        root_path_data_mentors=mentor_root,
        root_path_video_mentors=mentor_root,
    )
    expected_base_path = os.path.join(mentor_root, mentor_id)
    mock_isfile_with_paths(
        mock_isfile, [os.path.join(expected_base_path, p) for p in existing_files]
    )
    assert mpath.get_mentor_data() == expected_base_path
    u = Utterance(**utterance_dict)
    actual_path = mpath.find_asset(
        u, asset_type, return_non_existing_paths=return_non_existing_paths
    )
    expected_path = (
        os.path.join(expected_base_path, expected_rel_path) if expected_rel_path else ""
    )
    assert expected_path == actual_path
