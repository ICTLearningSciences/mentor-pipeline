import glob
import os
import ffmpy
import noisereduce as nr
import numpy as np
import soundfile as sf
from typing import Iterable, Union


def _reduce_noise(
    noise_sample: np.ndarray, f: Union[str, os.PathLike], decrease_by=0.5
):
    f = os.path.abspath(f)
    fpath, fext = os.path.splitext(f)
    audio_output_file = f"{fpath}.wav"
    audio_input_file = f"{fpath}-prenoisefix.wav"
    if fext != ".wav":
        ffmpy.FFmpeg(inputs={f: None}, outputs={audio_input_file: "-y -ac 1"}).run()
    data, rate = sf.read(audio_input_file)
    # noise_sample = data[0:1000]
    reduced_noise = nr.reduce_noise(
        audio_clip=data,
        noise_clip=noise_sample,
        prop_decrease=decrease_by,
        verbose=False,
    )
    sf.write(audio_output_file, reduced_noise, rate)
    if fext == ".mp4":
        tmp_file = f"{fpath}.tmp{fext}"
        ffmpy.FFmpeg(
            inputs={f: None, audio_output_file: None},
            outputs={tmp_file: "-y -c:v copy -map 0:v:0 -map 1:a:0"},
        ).run()
        os.rename(f, f"{fpath}-prenoisefix{fext}")
        os.rename(tmp_file, f)
        os.remove(audio_input_file)
        os.remove(audio_output_file)


def reduce_noise(
    noise_sample: str,
    files_to_fix: Union[str, Iterable[os.PathLike], os.PathLike],
    decrease_by=0.75,
):
    noise, _ = sf.read(noise_sample)
    for f in (
        glob.glob(str(files_to_fix))  # type: ignore
        if isinstance(files_to_fix, str)
        else files_to_fix
    ):
        _reduce_noise(noise, f, decrease_by=decrease_by)
