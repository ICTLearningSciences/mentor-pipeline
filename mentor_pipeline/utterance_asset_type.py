#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
from enum import Enum
import os
from typing import Callable, Dict, Optional

from mentor_pipeline.utterances import Utterance

_ASSET_TYPE_BY_PROP_NAME = dict()


def _convert_ext(p: str, new_ext: str) -> str:
    stem = os.path.splitext(p)[0]
    return f"{stem}.{new_ext}"


class MentorAssetRoot(Enum):
    DATA = 1
    VIDEOS = 2


class UtteranceAssetType:
    """
    Represents an asset type that a mentor utterance should possess.
    Generally DO NOT create instances of this class;
    instead use the instances exported by this module, e.g. SESSION_AUDIO
    """

    def __init__(
        self,
        name: str,
        mentor_asset_root: MentorAssetRoot,
        utterance_prop_name: str,
        default_file_ext: str,
        infer_path_from_props: Dict[str, Optional[Callable[[str], str]]] = None,
        infer_path_from_utterance: Callable[[Utterance], str] = None,
    ):
        self._name = name
        self._mentor_asset_root = mentor_asset_root
        self._utterance_prop_name = utterance_prop_name
        self._default_file_ext = default_file_ext
        self._infer_path_from_props = infer_path_from_props or {}
        self._infer_path_from_utterance = infer_path_from_utterance
        _ASSET_TYPE_BY_PROP_NAME[utterance_prop_name] = self

    def convert_ext(self, p: str) -> str:
        return _convert_ext(p, self.get_default_file_ext())

    def get_name(self) -> str:
        return self._name

    def get_utterance_val(self, u: Utterance) -> str:
        return (
            getattr(u, self._utterance_prop_name) if self._utterance_prop_name else None
        )

    def get_utterance_inferred_path(self, u: Utterance) -> str:
        for p, convert_func in self._infer_path_from_props.items():
            asset_type = _ASSET_TYPE_BY_PROP_NAME.get(p)
            if not asset_type:
                continue
            asset_path_from = asset_type.get_utterance_val(u)
            if asset_path_from:
                return (
                    convert_func(asset_path_from)
                    if convert_func
                    else self.convert_ext(asset_path_from)
                )
        return (
            self._infer_path_from_utterance(u)
            if self._infer_path_from_utterance
            else ""
        )

    def get_default_file_ext(self) -> str:
        return self._default_file_ext

    def get_mentor_asset_root(self) -> MentorAssetRoot:
        return self._mentor_asset_root


SESSION_AUDIO = UtteranceAssetType(
    "sessionAudio",
    MentorAssetRoot.DATA,
    "sessionAudio",
    "mp3",
    infer_path_from_props=dict(sessionTimestamps=None, sessionVideo=None),
)
SESSION_TIMESTAMPS = UtteranceAssetType(
    "sessionTimestamps",
    MentorAssetRoot.DATA,
    "sessionTimestamps",
    "csv",
    infer_path_from_props=dict(sessionVideo=None, sessionAudio=None),
)
SESSION_VIDEO = UtteranceAssetType(
    "sessionVideo",
    MentorAssetRoot.DATA,
    "sessionVideo",
    "mp4",
    infer_path_from_props=dict(sessionTimestamps=None, sessionAudio=None),
)
UTTERANCE_AUDIO = UtteranceAssetType(
    "sessionVideo",
    MentorAssetRoot.DATA,
    "utteranceAudio",
    "mp3",
    infer_path_from_props=dict(
        utteranceVideo=lambda p: _convert_ext(
            p.replace("utterance_video", "utterance_audio"), "mp3"
        )
    ),
    infer_path_from_utterance=lambda u: os.path.join(
        "build", "utterance_audio", f"{u.get_id()}.mp3"
    ),
)
UTTERANCE_VIDEO = UtteranceAssetType(
    "utteranceVideo",
    MentorAssetRoot.VIDEOS,
    "utteranceVideo",
    "mp4",
    infer_path_from_props=dict(
        utteranceAudio=lambda p: _convert_ext(
            p.replace("utterance_audio", "utterance_video"), "mp4"
        )
    ),
    infer_path_from_utterance=lambda u: os.path.join(
        "build", "utterance_video", f"{u.get_id()}.mp4"
    ),
)

UTTERANCE_VIDEO_MOBILE = UtteranceAssetType(
    "utteranceVideoMobile",
    MentorAssetRoot.VIDEOS,
    "",
    "mp4",
    infer_path_from_utterance=lambda u: os.path.join("mobile", f"{u.get_id()}.mp4"),
)

UTTERANCE_VIDEO_WEB = UtteranceAssetType(
    "utteranceVideoWeb",
    MentorAssetRoot.VIDEOS,
    "",
    "mp4",
    infer_path_from_utterance=lambda u: os.path.join("web", f"{u.get_id()}.mp4"),
)

UTTERANCE_CAPTIONS = UtteranceAssetType(
    "utteranceCaptions",
    MentorAssetRoot.DATA,
    "",
    "vtt",
    infer_path_from_utterance=lambda u: os.path.join(
        "data", "tracks", f"{u.get_id()}.vtt"
    ),
)
