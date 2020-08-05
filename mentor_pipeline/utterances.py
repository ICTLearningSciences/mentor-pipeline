# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
from dataclasses import asdict, dataclass, field
import math
from typing import Dict, List, Optional, Union

from mentor_pipeline.utils import yaml_load, yaml_write


def _to_slice_timestr(secs_total: float) -> str:
    m, s = divmod(secs_total, 60)
    h, m = divmod(m, 60)
    hs = int(round(secs_total - math.floor(secs_total), 2) * 100)
    return f"{int(h):02}{int(m):02}{int(s):02}{hs:02}"


def _utterance_id(session: int, part: int, time_start: float, time_end: float) -> str:
    return f"s{session:03}p{part:03}s{_to_slice_timestr(time_start)}e{_to_slice_timestr(time_end)}"


class TranscriptionType:
    ANSWER = "A"
    UTTERANCE = "U"


class UtteranceType:
    ANSWER = "_ANSWER_"
    FEEDBACK = "_FEEDBACK_"
    IDLE = "_IDLE_"
    INTRO = "_INTRO_"
    OFF_TOPIC = "_OFF_TOPIC_"
    PROFANITY = "_PROFANITY_"
    PROMPT = "_PROMPT_"
    REPEAT = "_REPEAT_"

    @classmethod
    def is_valid(cls, v: str) -> bool:
        # TODO: in python 3.7+ use real UtteranceType type above
        return v in vars(cls).values()

    @classmethod
    def get_required_types(cls) -> list:
        return [
            cls.FEEDBACK,
            cls.IDLE,
            cls.INTRO,
            cls.OFF_TOPIC,
            cls.PROMPT,
            cls.REPEAT,
        ]


@dataclass
class Utterance:
    errorMessage: str = ""
    mentor: str = ""
    question: str = ""
    paraphrases: List[str] = field(default_factory=lambda: [])
    part: int = 1
    session: int = 1
    sessionAudio: str = ""
    sessionTimestamps: str = ""
    sessionVideo: str = ""
    timeEnd: float = -1.0
    timeStart: float = -1.0
    topics: List[str] = field(default_factory=lambda: [])
    transcript: str = ""
    utteranceAudio: str = ""
    utteranceVideo: str = ""
    utteranceType: str = ""

    def get_duration(self) -> float:
        """
        returns duration in seconds if timeStart and timeEnd are set, else -1
        """
        return (
            self.timeEnd - self.timeStart
            if (self.timeStart >= 0 and self.timeEnd >= self.timeStart)
            else -1
        )

    def get_id(self) -> str:
        return _utterance_id(self.session, self.part, self.timeStart, self.timeEnd)

    def is_no_transcription_type(self) -> bool:
        return bool(self.utteranceType == UtteranceType.IDLE)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class UtteranceMap:
    utterancesById: Dict[str, Utterance] = field(default_factory=lambda: {})

    def __post_init__(self):
        self.utterancesById = {
            k: v if isinstance(v, Utterance) else Utterance(**v)
            for (k, v) in self.utterancesById.items()
        }

    def apply_timestamps(
        self,
        session: int,
        part: int,
        sessionTimestamps: str,
        timestampRows: List[Utterance],
    ) -> None:
        for u in timestampRows:
            self.utterancesById[u.get_id()] = u

    def find_by_id(self, uid) -> Optional[Utterance]:
        return self.utterancesById.get(uid)

    def find_one(
        self, session: int, part: int, time_start: float, time_end: float
    ) -> Optional[Utterance]:
        uid = _utterance_id(session, part, time_start, time_end)
        return self.utterancesById.get(uid)

    def set_transcript(self, uid: str, transcript: str, source_audio: str) -> None:
        if uid not in self.utterancesById:
            raise ValueError(
                f"set_transcript called with unknown utternace id: '{uid}'"
            )
        u = self.utterancesById[uid]
        u.transcript = transcript
        u.utteranceAudio = source_audio

    def to_dict(self):
        return asdict(self)

    def utterances(self) -> List[Utterance]:
        return sorted(
            self.utterancesById.values(), key=lambda u: (u.session, u.part, u.timeStart)
        )


def copy_utterance(u: Utterance) -> Utterance:
    return Utterance(**u.to_dict())


def copy_utterances(u: Union[UtteranceMap, dict]) -> UtteranceMap:
    return (
        UtteranceMap(**u.to_dict())
        if isinstance(u, UtteranceMap)
        else UtteranceMap(u)
        if isinstance(u, dict)
        else UtteranceMap()
    )


def utterance_map_from_list(utterances: List[Union[Utterance, dict]]) -> UtteranceMap:
    ulist = [u if isinstance(u, Utterance) else Utterance(**u) for u in utterances]
    return UtteranceMap(**dict(utterancesById={u.get_id(): u for u in ulist}))


def utterances_from_yaml(yml: str) -> UtteranceMap:
    d = yaml_load(yml)
    if "utterances" in d:
        ulist = [Utterance(**u) for u in d.get("utterances")]  # type: ignore
        return UtteranceMap(**dict(utterancesById={u.get_id(): u for u in ulist}))
    else:
        return UtteranceMap(**d)


def utterances_to_yaml(utterances: Union[UtteranceMap, dict], tgt_path: str) -> None:
    if isinstance(utterances, UtteranceMap):
        d = dict(utterances=[u.to_dict() for u in utterances.utterances()])
        return utterances_to_yaml(d, tgt_path)
    else:
        yaml_write(utterances, tgt_path)
