import logging
from typing import List

import transcribe

from mentor_pipeline.mentorpath import MentorPath
from mentor_pipeline.process import (
    prepare_videos_mobile,
    prepare_videos_web,
    sessions_to_audio,
    sync_timestamps,
    update_paraphrases,
    update_topics,
    update_transcripts,
    utterances_noise_reduction,
    utterances_slice_audio,
    utterances_slice_video,
    utterances_to_captions,
    utterances_to_topics_by_question,
    utterances_to_training_data,
)
from mentor_pipeline.topics import TopicsByQuestion


class Pipeline:
    def __init__(self, mentor: str, mentor_data_path: str):
        self.mpath = MentorPath(
            mentor_id=mentor, root_path_data_mentors=mentor_data_path
        )
        logging.getLogger().setLevel(logging.INFO)

    def data_update(self, force_update_transcripts: bool = False):
        transcription_service = transcribe.init_transcription_service()
        utterances_synced = sync_timestamps(self.mpath)
        s2a_result = sessions_to_audio(utterances_synced, self.mpath)
        utterances_w_audio_src = utterances_slice_audio(
            s2a_result.utterances, self.mpath
        )
        utterances_w_transcripts = update_transcripts(
            utterances_w_audio_src,
            transcription_service,
            self.mpath,
            force_update=force_update_transcripts,
        )
        utterances_w_paraphrases = update_paraphrases(
            utterances_w_transcripts,
            self.mpath.load_paraphrases_by_question_from_csv(
                allow_file_not_exists=True
            ),
        )
        utterances_w_topics = update_topics(
            utterances_w_paraphrases,
            self.mpath.load_topics_by_question_from_csv(allow_file_not_exists=True),
        )
        captions_result = utterances_to_captions(utterances_w_topics, self.mpath)
        td_result = utterances_to_training_data(captions_result.utterances)
        self.mpath.write_training_questions_paraphrases_answers(
            td_result.questions_paraphrases_answers
        )
        self.mpath.write_training_prompts_utterances(td_result.prompts_utterances)
        self.mpath.write_training_classifier_data(td_result.classifier_data)
        self.mpath.write_training_utterance_data(td_result.utterance_data)
        self.mpath.write_utterances(td_result.utterances)

    def sync_timestamps(self):
        utterances_new = sync_timestamps(self.mpath)
        print(f"utterances={utterances_new.to_dict()}")

    def topics_by_question_generate(
        self, mentors: List[str] = None
    ) -> TopicsByQuestion:
        utterances = self.mpath.load_utterances(create_new=False)
        assert utterances is not None
        tbq = utterances_to_topics_by_question(utterances)
        self.mpath.write_topics_by_question(tbq)
        return tbq

    def videos_update(self):
        utterances_init = self.mpath.load_utterances(create_new=False)
        if not utterances_init:
            logging.error(
                f"unable to run video update with no utterances. Try data_update first."
            )
            return
        utterances_w_video = utterances_slice_video(utterances_init, self.mpath)
        self.mpath.write_utterances(utterances_w_video)
        # TODO: add test for this
        utterances_w_noise_reduction = utterances_noise_reduction(
            utterances_w_video, self.mpath
        )
        utterances_w_video_mobile = prepare_videos_mobile(
            utterances_w_noise_reduction, self.mpath
        )
        utterances_w_video_web = prepare_videos_web(
            utterances_w_video_mobile, self.mpath
        )
        self.mpath.write_utterances(utterances_w_video_web)
