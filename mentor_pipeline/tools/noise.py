import os
import ffmpy
import noisereduce as nr
import numpy as np
import soundfile as sf
from typing import List


def _reduce_noise(noise_sample: np.ndarray, f: str):
    f = os.path.abspath(f)
    fpath, fext = os.path.splitext(f)
    save_file = f"{fpath}-prenoisefix{fext}"
    os.rename(f, save_file)
    audio_output_file = f"{fpath}.wav"
    audio_input_file = f"{fpath}-prenoisefix.wav"
    if fext != ".wav":
        ffmpy.FFmpeg(inputs={save_file: None}, outputs={audio_input_file: None}).run()
        print(f"used ffmpeg to create {audio_input_file} from {save_file}")
    print(f"fext={fext} audio_input_file={audio_input_file}")
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


def reduce_noise_batch(noise_sample: str, files_to_fix: List[str]):
    noise, _ = sf.read(noise_sample)
    for f in files_to_fix:
        _reduce_noise(noise, f)
