import glob
import os
import ffmpy
import noisereduce as nr
import numpy as np
import soundfile as sf
from typing import Iterable, Union


def _reduce_noise(noise_sample: np.ndarray, f: os.PathLike):
    f = os.path.abspath(f)
    fpath, fext = os.path.splitext(f)
    save_file = f"{fpath}-prenoisefix{fext}"
    os.rename(f, save_file)
    audio_output_file = f"{fpath}.wav"
    audio_input_file = f"{fpath}-prenoisefix.wav"
    if fext != ".wav":
        ffmpy.FFmpeg(inputs={save_file: None}, outputs={audio_input_file: None}).run()
    data, rate = sf.read(audio_input_file)
    reduced_noise = nr.reduce_noise(
        audio_clip=data, noise_clip=noise_sample, verbose=False
    )
    sf.write(audio_output_file, reduced_noise, rate)
    if fext == ".mp4":
        ffmpy.FFmpeg(
            inputs={save_file: None, audio_output_file: None},
            outputs={f: "-c:v copy -map 0:v:0 -map 1:a:0"},
        ).run()


def reduce_noise(
    noise_sample: str, files_to_fix: Union[Iterable[os.PathLike], os.PathLike]
):
    noise, _ = sf.read(noise_sample)
    for f in (
        glob.glob(str(files_to_fix))  # type: ignore
        if isinstance(files_to_fix, str)
        else files_to_fix
    ):
        _reduce_noise(noise, f)
