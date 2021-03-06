#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
from distutils.dir_util import copy_tree
import glob
import os
from shutil import copyfile
from tempfile import mkdtemp
from typing import List
from unittest.mock import Mock

from mentor_pipeline.mentorpath import MentorPath
from mentor_pipeline.utterances import UtteranceMap, utterances_from_yaml


def load_expected_utterances(
    mp: MentorPath, expected_utterances_file="expected-utterances.yaml"
) -> UtteranceMap:
    expected_utterance_path = mp.get_mentor_data(expected_utterances_file)
    assert os.path.isfile(
        expected_utterance_path
    ), f"assert_utterances_match_expected requires a yaml file of expected utterances at {expected_utterance_path}"
    return utterances_from_yaml(expected_utterance_path)


def copy_mentor_to_tmp(
    mentor: str, mentor_data_root: str, copy_root_sibling_files: str = "*.csv"
) -> MentorPath:
    tmp_mentors = mkdtemp()
    mentor_data_root_tgt = os.path.join(tmp_mentors, "data", "mentors")
    os.makedirs(mentor_data_root_tgt)
    mpath_src = MentorPath(mentor_id=mentor, root_path_data_mentors=mentor_data_root)
    mpath_tgt = MentorPath(
        mentor_id=mentor, root_path_data_mentors=mentor_data_root_tgt
    )
    src_mentor_data = mpath_src.get_mentor_data()
    tgt_mentor_data = mpath_tgt.get_mentor_data()
    copy_tree(src_mentor_data, tgt_mentor_data)
    if copy_root_sibling_files:
        for copy_src in glob.glob(
            mpath_src.get_root_path_data(copy_root_sibling_files)
        ):
            rel_path = os.path.relpath(copy_src, mpath_src.get_root_path_data())
            copy_tgt = mpath_tgt.get_root_path_data(rel_path)
            copyfile(copy_src, copy_tgt)
    src_mentor_videos = mpath_src.get_mentor_video()
    if os.path.isdir(src_mentor_videos):
        tgt_mentor_videos = mpath_tgt.get_mentor_video()
        os.makedirs(tgt_mentor_videos)
        copy_tree(src_mentor_videos, tgt_mentor_videos)
    return mpath_tgt


def resource_root_for_test(test_file: str) -> str:
    return os.path.abspath(
        os.path.join(
            ".", "tests", "fixtures", os.path.splitext(os.path.basename(test_file))[0]
        )
    )


def resource_root_mentors_for_test(test_file: str) -> str:
    return os.path.join(resource_root_for_test(test_file), "mentors")


def mock_isfile_with_paths(mock_isfile: Mock, true_paths: List[str]) -> Mock:
    mock_isfile.side_effect = lambda p: p in true_paths
    return mock_isfile
