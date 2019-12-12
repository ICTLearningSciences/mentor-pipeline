import os

from mentor_pipeline.mentorpath import MentorPath
from mentor_pipeline.process import (
    SessionToAudioResultSummary,
    session_to_audio_result_summary_from_yaml,
)
from mentor_pipeline.utterance_asset_type import UtteranceAssetType
from mentor_pipeline.utterances import Utterance, UtteranceMap

from .utils import load_expected_utterances


def assert_utterance_asset_exists(
    mp: MentorPath, u: Utterance, asset_type: UtteranceAssetType
) -> None:
    expected_path = mp.find_asset(u, asset_type, return_non_existing_paths=True)
    assert os.path.isfile(
        expected_path
    ), "expected file for utterance {} and asset type {} at path {}".format(
        u.get_id(), asset_type.get_name(), expected_path
    )


def assert_session_to_audio_result_summary_match_expected(
    mp: MentorPath,
    actual_data: SessionToAudioResultSummary,
    expected_data_file="expected-session-to-audio-summary.yaml",
) -> None:
    """
    Test helper to assert that summary for process.session_to_audio match expected for a mentorpath

    Args:
    - mp: the MentorPath
    - actual_data: SessionToAudioResultSummary
    - expected_file: path to the location of the expected-utterances (stored in yaml)
    """
    expected_data_path = mp.get_mentor_data(expected_data_file)
    assert os.path.isfile(
        expected_data_path
    ), f"requires a yaml file of expected summary for SessionToAudioResultSummary at {expected_data_path}"
    expected_data = session_to_audio_result_summary_from_yaml(expected_data_path)
    assert expected_data.to_dict() == actual_data.to_dict()


def assert_utterances_match_expected(
    mp: MentorPath,
    utterances: UtteranceMap = None,
    expected_utterances_file: str = "expected-utterances.yaml",
) -> None:
    """
    Test helper to assert that utterances match expected for a mentorpath

    Args:
    - mp: the MentorPath
    - utterances: the actual utterances, if not passed will look for utterances at the default mentorpath location
    - expected_utterances_file: path to the location of the expected-utterances (stored in yaml)
    """
    utterances = utterances or mp.load_utterances()
    assert isinstance(
        utterances, UtteranceMap
    ), f"should be utterances file at {mp.get_utterances_data_path()}"
    expected_utterances = load_expected_utterances(mp, expected_utterances_file)
    assert expected_utterances.to_dict() == utterances.to_dict()
