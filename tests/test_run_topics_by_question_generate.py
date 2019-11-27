import pytest

from .helpers import (
    copy_mentor_to_tmp,
    resource_root_mentors_for_test,
)
from mentor_pipeline.run import Pipeline


MENTOR_ROOT = resource_root_mentors_for_test(__file__)


@pytest.mark.parametrize("mentor_root,mentor_id", [(MENTOR_ROOT, "mentor1")])
def test_it_generates_topics_by_question(
    mentor_root: str, mentor_id: str,
):
    mpath = copy_mentor_to_tmp(mentor_id, mentor_root)
    p = Pipeline(mentor_id, mpath.root_path_data_mentors)
    p.topics_by_question_generate(mentors=[mentor_id])
    actual_topics_by_question = mpath.load_topics_by_question_from_csv()
    expected_topics_by_question = mpath.load_topics_by_question_from_csv(
        file_name="expected_topics_by_question.csv"
    )
    assert expected_topics_by_question.to_dict() == actual_topics_by_question.to_dict()
