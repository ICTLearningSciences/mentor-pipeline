import os
import logging
from typing import Callable, List, Optional
from uuid import uuid1

from watson_developer_cloud import SpeechToTextV1

from . import (
    copy_shallow,
    transcribe_requests_to_result,
    TranscribeBatchResult,
    TranscribeJobRequest,
    TranscribeJobStatus,
    TranscribeJobsUpdate,
    TranscriptionService,
)


class WatsonTranscriptionService(TranscriptionService):
    def init_service(self):
        """
        API credentials for the IBM Watson service are given below
        Web login credentials for https://console.ng.bluemix.net/
        Credentials File: Ask Ben Nye for it
        Place the text file containing the credentials file in the root of the website version code
        Contact Madhusudhan Krishnamachari at madhusudhank@icloud.com to get assistance on how to use Watson. (IBM Documentation should help)
        """
        username = os.environ["WATSON_USERNAME"]
        password = os.environ["WATSON_PASSWORD"]

        if not (username and password):
            raise (Exception("missing WATSON_USERNAME or WATSON_PASSWORD"))
        else:
            self.speech_to_text = SpeechToTextV1(username=username, password=password)
            # tell IBM Watson not to collect our data
            self.speech_to_text.set_default_headers(
                {"x-watson-learning-opt-out": "true"}
            )

    def _transcribe_one(self, audio_file: str) -> str:
        """
        Opens an audio .ogg file and calls the recognize function which transcribes the audio to text. That is stored in the `result` variable.
        The result variable is a dictionary which contains sentences of transcriptions. We cycle through the result variable to get the actual text.

        Note: Please make sure that the audio file is less than 100 MB in size. IBM Watson can't handle files larger than 100 MB.
        For this project, the duration of each Q-A won't exceed 5 minutes and in that case, it will be well within 100 MB.
        """
        if not self.speech_to_text:
            self.init_service()
        with open(audio_file, "rb") as f:
            result = self.speech_to_text.recognize(
                f, content_type="audio/mp3", continuous=True
            ).result["results"]
            transcript = "".join(
                item["alternatives"][0]["transcript"] for item in result
            )
            return transcript

    def transcribe(
        self,
        transcribe_requests: List[TranscribeJobRequest],
        batch_id: str = "",
        poll_interval=5,
        on_update: Optional[Callable[[TranscribeJobsUpdate], None]] = None,
    ) -> TranscribeBatchResult:
        batch_id = batch_id or str(uuid1())
        result = transcribe_requests_to_result(
            transcribe_requests, initial_status=TranscribeJobStatus.QUEUED
        )
        for r in transcribe_requests:
            result = copy_shallow(result)
            rid = r.get_fq_id()
            try:
                transcript = self._transcribe_one(r.sourceFile)
                result.update_job(
                    rid, status=TranscribeJobStatus.SUCCEEDED, transcript=transcript
                )
                if on_update:
                    on_update(TranscribeJobsUpdate(result=result, idsUpdated=[rid]))
            except Exception as ex:
                logging.exception(
                    f"Failed to transcribe {r.sourceFile} with error: {ex}"
                )
                result.update_job(rid, status=TranscribeJobStatus.FAILED, error=str(ex))
                if on_update:
                    on_update(TranscribeJobsUpdate(result=result, idsUpdated=[rid]))
        return result
