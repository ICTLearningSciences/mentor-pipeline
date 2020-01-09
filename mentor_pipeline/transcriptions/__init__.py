from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
import enum
from importlib import import_module

import os
from typing import Any, Callable, Dict, Iterable, List, Optional, Union

import pytest

# we want to have pytest assert introspection in the helpers
pytest.register_assert_rewrite("mentor_pipeline.transcriptions.mock")


class MissingRequiredEnvVarError(Exception):
    pass


def require_env(n: str, v: str) -> str:
    v = v or os.environ.get(n, "")
    if not v:
        raise MissingRequiredEnvVarError(f"missing required env var '{n}'")
    return v


class TranscribeJobStatus(enum.Enum):
    NONE = 0
    UPLOADING = 1
    UPLOADED = 2
    QUEUED = 3
    IN_PROGRESS = 4
    SUCCEEDED = 5
    FAILED = 6


@dataclass
class TranscribeJob:
    batchId: str
    jobId: str
    sourceFile: str
    mediaFormat: str
    status: TranscribeJobStatus = TranscribeJobStatus.NONE
    transcript: str = ""
    error: str = ""
    info: Dict[str, str] = field(default_factory=lambda: {})

    def __post_init__(self):
        self.transcript = self.transcript or ""
        if isinstance(self.status, str):
            self.status = TranscribeJobStatus[str(self.status)]

    def get_fq_id(self) -> str:
        return f"{self.batchId}-{self.jobId}"

    def is_resolved(self) -> bool:
        return bool(
            self.status in [TranscribeJobStatus.SUCCEEDED, TranscribeJobStatus.FAILED]
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class TranscribeJobRequest:
    batchId: str
    jobId: str
    sourceFile: str
    mediaFormat: str = ""
    language_code: str = ""

    def get_fq_id(self) -> str:
        return f"{self.batchId}-{self.jobId}"

    def get_media_format(self):
        return self.mediaFormat or os.path.splitext(self.sourceFile)[1][1:]

    def get_language_code(self, default_language_code: str = "en-US") -> str:
        return self.language_code or default_language_code

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_job(
        self, status: TranscribeJobStatus = TranscribeJobStatus.NONE
    ) -> TranscribeJob:
        return TranscribeJob(
            batchId=self.batchId,
            jobId=self.jobId,
            sourceFile=self.sourceFile,
            mediaFormat=self.get_media_format(),
        )


@dataclass
class TranscribeBatchResultSummary:
    jobCountsByStatus: Dict[TranscribeJobStatus, int] = field(
        default_factory=lambda: {}
    )

    def get_count(
        self, statuses: Union[TranscribeJobStatus, Iterable[TranscribeJobStatus]]
    ) -> int:
        if isinstance(statuses, TranscribeJobStatus):
            return self.jobCountsByStatus.get(statuses, 0)
        n = 0
        assert isinstance(statuses, Iterable)
        for s in statuses:
            n = n + self.get_count(s)
        return n

    def get_count_completed(self) -> int:
        return self.get_count(
            [TranscribeJobStatus.SUCCEEDED, TranscribeJobStatus.FAILED]
        )

    def increment(self, status: TranscribeJobStatus) -> int:
        n = self.get_count(status) + 1
        self.jobCountsByStatus[status] = n
        return n


@dataclass
class TranscribeBatchResult:
    transcribeJobsById: Dict[str, TranscribeJob] = field(default_factory=lambda: {})

    def __post_init__(self):
        self.transcribeJobsById = {
            k: v if isinstance(v, TranscribeJob) else TranscribeJob(**v)
            for (k, v) in self.transcribeJobsById.items()
        }

    def has_any_unresolved(self) -> bool:
        return (
            False
            if all(j.is_resolved() for j in self.transcribeJobsById.values())
            else True
        )

    def job_completed(self, id: str, status: TranscribeJobStatus) -> bool:
        if id not in id in self.transcribeJobsById:
            return False
        j = self.transcribeJobsById.get(id)
        return bool(
            j
            and j.status in [TranscribeJobStatus.SUCCEEDED, TranscribeJobStatus.FAILED]
        )

    def jobs(self) -> Iterable[TranscribeJob]:
        return self.transcribeJobsById.values()

    def summary(self) -> TranscribeBatchResultSummary:
        result = TranscribeBatchResultSummary()
        for j in self.jobs():
            result.increment(j.status)
        return result

    def update_job(
        self,
        id: str,
        status: TranscribeJobStatus = TranscribeJobStatus.NONE,
        info: Dict[str, str] = {},
        transcript: str = "",
        error: str = "",
    ) -> bool:
        if id not in self.transcribeJobsById:
            raise Exception(f"update for untracked transcribe job id '{id}'")
        job_cur = self.transcribeJobsById.get(id)
        assert job_cur is not None
        if job_cur.status == status:
            return False
        job_updated = TranscribeJob(**job_cur.to_dict())
        job_updated.status = status or TranscribeJobStatus.NONE
        job_updated.transcript = transcript or ""
        job_updated.error = error or ""
        job_updated.info = info or {}
        self.transcribeJobsById[id] = job_updated
        return True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "transcribeJobsById": {
                k: v.to_dict() for k, v in self.transcribeJobsById.items()
            }
        }


@dataclass
class TranscribeJobsUpdate:
    result: TranscribeBatchResult = field(
        default_factory=lambda: TranscribeBatchResult()
    )
    idsUpdated: List[str] = field(default_factory=lambda: [])

    def __post_init__(self):
        if isinstance(self.result, dict):
            self.result = TranscribeBatchResult(**self.result)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "result": self.result.to_dict(),
            "idsUpdated": [i for i in self.idsUpdated],
        }


def copy_shallow(r: TranscribeBatchResult) -> TranscribeBatchResult:
    return TranscribeBatchResult(
        transcribeJobsById={k: v for k, v in r.transcribeJobsById.items()}
    )


def transcribe_jobs_to_result(jobs: List[TranscribeJob]) -> TranscribeBatchResult:
    return TranscribeBatchResult(transcribeJobsById={j.get_fq_id(): j for j in jobs})


def transcribe_requests_to_result(
    transcribe_requests: List[TranscribeJobRequest],
    initial_status: TranscribeJobStatus = TranscribeJobStatus.NONE,
) -> TranscribeBatchResult:
    return TranscribeBatchResult(
        transcribeJobsById={r.get_fq_id(): r.to_job() for r in transcribe_requests}
    )


class TranscriptionService(ABC):
    @abstractmethod
    def init_service(self) -> None:
        raise NotImplementedError()

    @abstractmethod
    def transcribe(
        self,
        transcribe_requests: List[TranscribeJobRequest],
        batch_id: str = "",
        poll_interval=5,
        on_update: Optional[Callable[[TranscribeJobsUpdate], None]] = None,
    ) -> TranscribeBatchResult:
        raise NotImplementedError()


def init_transcription_service() -> TranscriptionService:
    m = import_module(f"mentor_pipeline.transcriptions.watson")
    s = m.WatsonTranscriptionService()  # type: ignore
    s.init_service()
    return s
