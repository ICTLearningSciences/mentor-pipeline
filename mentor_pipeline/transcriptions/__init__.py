from abc import ABC, abstractmethod
from importlib import import_module


class TranscriptionService(ABC):
    @abstractmethod
    def transcribe(self, audio_file: str) -> str:
        raise NotImplementedError()

    @abstractmethod
    def init_service(self) -> None:
        raise NotImplementedError()


def init_transcription_service() -> TranscriptionService:
    m = import_module(f"mentor_pipeline.transcriptions.watson")
    s = m.WatsonTranscriptionService()  # type: ignore
    s.init_service()
    return s
