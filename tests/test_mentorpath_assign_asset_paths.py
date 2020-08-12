#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
import os

import pytest

from mentor_pipeline.mentorpath import MentorPath
from mentor_pipeline.utterances import Utterance


MENTOR_DATA_ROOT = os.path.abspath(
    os.path.join(
        ".", "tests", "fixtures", "test_mentorpath_assign_asset_paths", "mentors"
    )
)


@pytest.mark.parametrize("mentor_data_root,mentor_id", [(MENTOR_DATA_ROOT, "mentor1")])
def test_it_assigns_session_asset_paths_for_existing_assets_when_session_timestamps_set(
    mentor_data_root: str, mentor_id: str
):
    mpath = MentorPath(mentor_id=mentor_id, root_path_data_mentors=mentor_data_root)
    u1 = mpath.find_and_assign_assets(
        Utterance(sessionTimestamps="build/recordings/session1/p1-some-questions.csv")
    )
    assert "build/recordings/session1/p1-some-questions.mp3" == u1.sessionAudio
    assert "build/recordings/session1/p1-some-questions.csv" == u1.sessionTimestamps
    assert "build/recordings/session1/p1-some-questions.mp4" == u1.sessionVideo


@pytest.mark.parametrize("mentor_data_root,mentor_id", [(MENTOR_DATA_ROOT, "mentor1")])
def test_it_assigns_session_asset_paths_for_existing_assets_when_session_video_set(
    mentor_data_root: str, mentor_id: str
):
    mpath = MentorPath(mentor_id=mentor_id, root_path_data_mentors=mentor_data_root)
    u1 = mpath.find_and_assign_assets(
        Utterance(sessionVideo="build/recordings/session1/p1-some-questions.mp4")
    )
    assert "build/recordings/session1/p1-some-questions.mp3" == u1.sessionAudio
    assert "build/recordings/session1/p1-some-questions.csv" == u1.sessionTimestamps
    assert "build/recordings/session1/p1-some-questions.mp4" == u1.sessionVideo


@pytest.mark.parametrize("mentor_data_root,mentor_id", [(MENTOR_DATA_ROOT, "mentor1")])
def test_it_assigns_session_asset_paths_for_existing_assets_when_session_audio_set(
    mentor_data_root: str, mentor_id: str
):
    mpath = MentorPath(mentor_id=mentor_id, root_path_data_mentors=mentor_data_root)
    u1 = mpath.find_and_assign_assets(
        Utterance(sessionAudio="build/recordings/session1/p1-some-questions.mp3")
    )
    assert "build/recordings/session1/p1-some-questions.mp3" == u1.sessionAudio
    assert "build/recordings/session1/p1-some-questions.csv" == u1.sessionTimestamps
    assert "build/recordings/session1/p1-some-questions.mp4" == u1.sessionVideo


@pytest.mark.parametrize(
    "mentor_data_root,mentor_id", [(MENTOR_DATA_ROOT, "mentor-missing-timestamps")]
)
def test_it_does_not_assign_session_timestamps_when_missing(
    mentor_data_root: str, mentor_id: str
):
    mpath = MentorPath(mentor_id=mentor_id, root_path_data_mentors=mentor_data_root)
    u1 = mpath.find_and_assign_assets(
        Utterance(sessionAudio="build/recordings/session1/p1-some-questions.mp3")
    )
    assert "build/recordings/session1/p1-some-questions.mp3" == u1.sessionAudio
    assert bool(u1.sessionTimestamps) is False
    assert "build/recordings/session1/p1-some-questions.mp4" == u1.sessionVideo


@pytest.mark.parametrize(
    "mentor_data_root,mentor_id", [(MENTOR_DATA_ROOT, "mentor-missing-video")]
)
def test_it_does_not_assign_session_video_when_missing(
    mentor_data_root: str, mentor_id: str
):
    mpath = MentorPath(mentor_id=mentor_id, root_path_data_mentors=mentor_data_root)
    u1 = mpath.find_and_assign_assets(
        Utterance(sessionAudio="build/recordings/session1/p1-some-questions.mp3")
    )
    assert "build/recordings/session1/p1-some-questions.mp3" == u1.sessionAudio
    assert "build/recordings/session1/p1-some-questions.csv" == u1.sessionTimestamps
    assert bool(u1.sessionVideo) is False


@pytest.mark.parametrize(
    "mentor_data_root,mentor_id", [(MENTOR_DATA_ROOT, "mentor-missing-audio")]
)
def test_it_does_not_assign_session_audio_when_missing(
    mentor_data_root: str, mentor_id: str
):
    mpath = MentorPath(mentor_id=mentor_id, root_path_data_mentors=mentor_data_root)
    u1 = mpath.find_and_assign_assets(
        Utterance(sessionVideo="build/recordings/session1/p1-some-questions.mp4")
    )
    assert bool(u1.sessionAudio) is False
    assert "build/recordings/session1/p1-some-questions.csv" == u1.sessionTimestamps
    assert "build/recordings/session1/p1-some-questions.mp4" == u1.sessionVideo
