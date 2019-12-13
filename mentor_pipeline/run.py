import logging
from typing import List

import mentor_pipeline
from mentor_pipeline.mentorpath import MentorPath
from mentor_pipeline.process import (
    transcripts_polish,
    prepare_videos_mobile,
    prepare_videos_web,
    sessions_to_audio,
    sync_timestamps,
    update_paraphrases,
    update_topics,
    update_transcripts,
    utterances_slice_audio,
    utterances_slice_video,
    utterances_to_captions,
    utterances_to_topics_by_question,
    utterances_to_training_data,
)
from mentor_pipeline.topics import TopicsByQuestion
from mentor_pipeline.utterances import UtteranceMap


class Pipeline:

    mpath: MentorPath = None

    def __init__(self, mentor: str, mentor_data_path: str):
        self.mpath = MentorPath(
            mentor_id=mentor, root_path_data_mentors=mentor_data_path
        )
        logging.getLogger().setLevel(logging.INFO)

    def sync_timestamps(self):
        utterances_new = sync_timestamps(self.mpath)
        print(f"utterances={utterances_new.to_dict()}")

    def _write_all_data_files(self, utterances: UtteranceMap) -> None:
        captions_result = utterances_to_captions(utterances, self.mpath)
        td_result = utterances_to_training_data(captions_result.utterances)
        self.mpath.write_training_questions_paraphrases_answers(
            td_result.questions_paraphrases_answers
        )
        self.mpath.write_training_prompts_utterances(td_result.prompts_utterances)
        self.mpath.write_training_classifier_data(td_result.classifier_data)
        self.mpath.write_training_utterance_data(td_result.utterance_data)
        self.mpath.write_utterances(td_result.utterances)

    def data_update(self):
        transcription_service = (
            mentor_pipeline.transcriptions.init_transcription_service()
        )
        utterances_synced = sync_timestamps(self.mpath)
        s2a_result = sessions_to_audio(utterances_synced, self.mpath)
        utterances_w_audio_src = utterances_slice_audio(
            s2a_result.utterances, self.mpath
        )
        utterances_w_transcripts = update_transcripts(
            utterances_w_audio_src, transcription_service, self.mpath
        )
        utterances_with_transcripts_polished = transcripts_polish(
            utterances_w_transcripts, self.mpath
        )
        utterances_w_paraphrases = update_paraphrases(
            utterances_with_transcripts_polished,
            self.mpath.load_paraphrases_by_question_from_csv(
                allow_file_not_exists=True
            ),
        )
        utterances_w_topics = update_topics(
            utterances_w_paraphrases,
            self.mpath.load_topics_by_question_from_csv(allow_file_not_exists=True),
        )
        self._write_all_data_files(utterances_w_topics)

    def transcripts_polish(self):
        utterances = self.mpath.load_utterances()
        utterances_with_transcripts_polished = transcripts_polish(
            utterances, self.mpath
        )
        self._write_all_data_files(utterances_with_transcripts_polished)

    def videos_update(self):
        utterances_init = self.mpath.load_utterances(create_new=False)
        if not utterances_init:
            logging.error(
                f"unable to run video update with no utterances. Try data_update first."
            )
            return
        utterances_w_video = utterances_slice_video(utterances_init, self.mpath)
        self.mpath.write_utterances(utterances_w_video)
        utterances_w_video_mobile = prepare_videos_mobile(
            utterances_w_video, self.mpath
        )
        utterances_w_video_web = prepare_videos_web(
            utterances_w_video_mobile, self.mpath
        )
        self.mpath.write_utterances(utterances_w_video_web)

    def topics_by_question_generate(
        self, mentors: List[str] = None
    ) -> TopicsByQuestion:
        utterances = self.mpath.load_utterances(create_new=False)
        tbq = utterances_to_topics_by_question(utterances)
        self.mpath.write_topics_by_question(tbq)
        return tbq
