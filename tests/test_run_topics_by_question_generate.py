#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
import pytest

from .helpers import copy_mentor_to_tmp, resource_root_mentors_for_test
from mentor_pipeline.run import Pipeline


MENTOR_ROOT = resource_root_mentors_for_test(__file__)


@pytest.mark.parametrize("mentor_root,mentor_id", [(MENTOR_ROOT, "mentor1")])
def test_it_generates_topics_by_question(mentor_root: str, mentor_id: str):
    mpath = copy_mentor_to_tmp(mentor_id, mentor_root)
    p = Pipeline(mentor_id, mpath.root_path_data_mentors)
    p.topics_by_question_generate(mentors=[mentor_id])
    actual_topics_by_question = mpath.load_topics_by_question_from_csv()
    expected_topics_by_question = mpath.load_topics_by_question_from_csv(
        file_name="expected_topics_by_question.csv"
    )
    assert expected_topics_by_question.to_dict() == actual_topics_by_question.to_dict()
