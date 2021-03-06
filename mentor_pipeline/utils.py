#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
import os
import yaml

try:
    from yaml import CLoader as YamlLoader
except ImportError:
    from yaml import Loader as YamlLoader  # type: ignore
import pandas as pd


def convert_to_seconds(time: str) -> float:
    """
    Converts a timestamp from HH:MM:SS or MM:SS to seconds.
    For example, a time 01:03:45 is 01*3600 + 03*60 + 45 = 3825 seconds

    Parameters:
    time: time string
    """
    time_adjustments = [3600, 60, 1, 0.01]
    time_split = time.split(":")
    if len(time_split) == 2:  # TODO: Remove this when data is standardized
        time_split.insert(0, "00")
    result = sum(s * float(a) for s, a in zip(time_adjustments, time_split))
    return float(f"{result:10.2f}")


def load_timestamp_data(filename, convert_timestamps_to_seconds=True):
    # Pandas reads empty cells as 0, replace with empty string
    timestamps_file = pd.read_csv(filename).fillna("")
    rows = range(0, len(timestamps_file))
    text_type = [timestamps_file.iloc[i]["Answer/Utterance"] for i in rows]
    questions = [timestamps_file.iloc[i]["Question"] for i in rows]
    start_times = [timestamps_file.iloc[i]["Response start"] for i in rows]
    end_times = [timestamps_file.iloc[i]["Response end"] for i in rows]
    start_times = (
        [convert_to_seconds(time) for time in start_times]
        if convert_timestamps_to_seconds
        else start_times
    )
    end_times = (
        [convert_to_seconds(time) for time in end_times]
        if convert_timestamps_to_seconds
        else end_times
    )
    return text_type, questions, start_times, end_times


def yaml_write(to_write: dict, write_path: str) -> None:
    """
    Writes a dictionary to a given path in yaml format.
    Mainly broken out as a utility for convenience of mocking in tests.
    """
    os.makedirs(os.path.dirname(write_path), exist_ok=True)
    with open(write_path, "w") as f:
        yaml.dump(to_write, f)


def yaml_load(from_path: str) -> dict:
    """
    Reads a dictionary from a given yaml file.
    Mainly broken out as a utility for convenience of mocking in tests,
    but also to handle in a single place the specific way
    that Loader must be imported and passed
    """
    with open(from_path, "r") as f:
        return yaml.load(f, Loader=YamlLoader)
