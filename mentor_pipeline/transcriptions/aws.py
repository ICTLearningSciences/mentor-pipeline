import logging
import requests
import os
from typing import Any, Callable, Dict, List, Optional
from time import sleep

import boto3
from uuid import uuid1

from botocore.exceptions import ClientError
from boto3_type_annotations.s3 import Client as S3Client
from boto3_type_annotations.transcribe import Client as TranscribeClient

from . import (
    copy_shallow,
    require_env,
    TranscribeBatchResult,
    TranscribeJobRequest,
    TranscribeJobsUpdate,
    TranscribeJobStatus,
)

_TRANSCRIBE_JOB_STATUS_BY_AWS_STATUS: Dict[str, TranscribeJobStatus] = {
    "QUEUED": TranscribeJobStatus.QUEUED,
    "IN_PROGRESS": TranscribeJobStatus.IN_PROGRESS,
    "FAILED": TranscribeJobStatus.FAILED,
    "COMPLETED": TranscribeJobStatus.SUCCEEDED,
}


def _create_s3_client(
    aws_access_key_id: str = "", aws_secret_access_key: str = "", aws_region: str = ""
) -> S3Client:
    return boto3.client(
        "s3",
        region_name=require_env("AWS_REGION", aws_region),
        aws_access_key_id=require_env("AWS_ACCESS_KEY_ID", aws_access_key_id),
        aws_secret_access_key=require_env(
            "AWS_SECRET_ACCESS_KEY", aws_secret_access_key
        ),
    )


def _create_transcribe_client(
    aws_access_key_id: str = "", aws_secret_access_key: str = "", aws_region: str = ""
) -> TranscribeClient:
    return boto3.client(
        "transcribe",
        region_name=require_env("AWS_REGION", aws_region),
        aws_access_key_id=require_env("AWS_ACCESS_KEY_ID", aws_access_key_id),
        aws_secret_access_key=require_env(
            "AWS_SECRET_ACCESS_KEY", aws_secret_access_key
        ),
    )


def _parse_aws_status(
    aws_status: str, default_status: TranscribeJobStatus = TranscribeJobStatus.NONE
) -> TranscribeJobStatus:
    return _TRANSCRIBE_JOB_STATUS_BY_AWS_STATUS.get(aws_status, default_status)


def _s3_file_exists(s3: S3Client, bucket: str, key: str) -> bool:
    try:
        s3.head_object(Bucket=bucket, Key=key)
    except ClientError as e:
        logging.error(e)
        return int(e.response["Error"]["Code"]) != 404
    return True


class AWSTranscriptionService:
    def __init__(
        self,
        s3_bucket: str,
        aws_access_key_id: str = "",
        aws_secret_access_key: str = "",
        aws_region: str = "",
        s3_root_path: str = "",
    ):
        self.aws_region = aws_region or require_env("AWS_REGION", aws_region)
        self.s3_bucket = s3_bucket
        self.s3_root_path = os.environ.get("S3_ROOT_PATH", "transcribe-source")
        self.s3_client = _create_s3_client(
            aws_region=self.aws_region,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )
        self.transcribe_client = _create_transcribe_client(
            aws_region=self.aws_region,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )

    def _get_batch_status(self, batch_id: str) -> List[Dict[str, Any]]:
        result: List[Dict[str, Any]] = []
        cur_result_page = self.transcribe_client.list_transcription_jobs(
            JobNameContains=batch_id
        )
        while True:
            cur_result_summaries: List[Dict[str, Any]] = cur_result_page.get(
                "TranscriptionJobSummaries"
            )
            for r in cur_result_summaries:
                result.append(r)
            next_token = cur_result_page.get("NextToken", "")
            if not next_token:
                break
            cur_result_page = self.transcribe_client.list_transcription_jobs(
                JobNameContains=batch_id, NextToken=next_token
            )
        return result

    def _load_transcript(self, aws_job_name: str) -> str:
        aws_job = self.transcribe_client.get_transcription_job(aws_job_name)
        if "TranscriptionJob" not in aws_job:
            raise Exception("Aws result has no 'TranscriptionJob'")
        if "Transcript" not in aws_job["TranscriptionJob"]:
            raise Exception("Aws result has no 'Transcript'")
        if "TranscriptFileUri" not in aws_job["TranscriptionJob"]["Transcript"]:
            raise Exception("Aws job Transcript has no 'TranscriptFileUrl'")
        url = aws_job["TranscriptionJob"]["Transcript"]["TranscriptFileUri"]
        transcript_res = requests.get(url)
        transcript_res.raise_for_status()
        transcript = transcript_res.json().get("Transcript")
        return transcript

    def get_s3_path(self, source_file: str, id: str) -> str:
        return f"{self.s3_root_path}/{id.lower()}{os.path.splitext(source_file)[1]}"

    def transcribe(
        self,
        transcribe_requests: List[TranscribeJobRequest],
        batch_id: str = "",
        poll_interval=5,
        on_update: Optional[Callable[[TranscribeJobsUpdate], None]] = None,
    ) -> TranscribeBatchResult:
        batch_id = batch_id or str(uuid1())
        result = TranscribeBatchResult(
            transcribeJobsById={r.get_fq_id(): r.to_job() for r in transcribe_requests}
        )
        for r in transcribe_requests:
            item_s3_path = self.get_s3_path(r.sourceFile, r.get_fq_id())
            self.s3_client.upload_file(
                r.sourceFile,
                self.s3_bucket,
                item_s3_path,
                ExtraArgs={"ACL": "public-read"},
            )
            self.transcribe_client.start_transcription_job(
                TranscriptionJobName=r.get_fq_id(),
                LanguageCode=r.get_language_code(),
                Media={
                    "MediaFileUri": f"https://s3.{self.aws_region}.amazonaws.com/{self.s3_bucket}/{item_s3_path}"
                },
                MediaFormat=r.get_media_format(),
            )
        while result.has_any_unresolved():
            if poll_interval > 0:
                sleep(poll_interval)
            job_updates = self._get_batch_status(batch_id)
            idsUpdated: List[str] = []
            result = copy_shallow(result)
            for ju in job_updates:
                try:
                    jid = ju.get("TranscriptionJobName", "")
                    jstatus = _parse_aws_status(
                        ju.get("TranscriptionJobStatus", ""),
                        default_status=TranscribeJobStatus.NONE,
                    )
                    if jstatus == TranscribeJobStatus.NONE:
                        raise ValueError(
                            f"job status has unknown value of {ju.get('TranscriptionJobStatus')}"
                        )
                    if result.job_completed(jid, jstatus):
                        continue
                    transcript = (
                        self._load_transcript(jid)
                        if jstatus == TranscribeJobStatus.SUCCEEDED
                        else ""
                    )
                    if result.update_job(jid, status=jstatus, transcript=transcript):
                        idsUpdated.append(jid)
                except Exception as ex:
                    logging.exception(f"failed to handle update  for {ju}: {ex}")
        return result
