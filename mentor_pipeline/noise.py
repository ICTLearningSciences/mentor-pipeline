#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
import glob
import os
import ffmpy
import noisereduce as nr
import numpy as np
import shutil
import soundfile as sf
from typing import Iterable, Union


def _reduce_noise(noise_sample: np.ndarray, f: Union[str, os.PathLike]):
    f = os.path.abspath(f)
    fpath, fext = os.path.splitext(f)
    save_file = f"{fpath}-prenoisefix{fext}"
    os.rename(f, save_file)
    audio_output_file = f"{fpath}.wav"
    audio_input_file = f"{fpath}-prenoisefix.wav"
    if fext != ".wav":
        ffmpy.FFmpeg(
            inputs={save_file: None},
            outputs={audio_input_file: "-acodec pcm_s16le -ac 1 -ar 16000"},
        ).run()
    data, rate = sf.read(audio_input_file)
    reduced_noise = nr.reduce_noise(
        audio_clip=data, noise_clip=noise_sample, prop_decrease=0.85, verbose=False
    )
    sf.write(audio_output_file, reduced_noise, rate)
    if fext == ".mp4":
        ffmpy.FFmpeg(
            inputs={save_file: None, audio_output_file: None},
            outputs={f: "-c:v copy -map 0:v:0 -map 1:a:0"},
        ).run()


def reduce_noise(
    noise_sample: str, files_to_fix: Union[str, Iterable[os.PathLike], os.PathLike]
):
    noise_sample_sav = f"{noise_sample}.sav"
    shutil.move(noise_sample, noise_sample_sav)
    ffmpy.FFmpeg(
        inputs={noise_sample_sav: None},
        outputs={noise_sample: "-acodec pcm_s16le -ac 1 -ar 16000"},
    ).run()
    noise, _ = sf.read(noise_sample)
    for f in (
        glob.glob(str(files_to_fix))  # type: ignore
        if isinstance(files_to_fix, str)
        else files_to_fix
    ):
        _reduce_noise(noise, f)
