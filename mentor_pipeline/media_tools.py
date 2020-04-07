import os
import re
import subprocess

import ffmpy
from pymediainfo import MediaInfo


def find_video_dims(video_file):
    media_info = MediaInfo.parse(video_file)
    video_tracks = [t for t in media_info.tracks if t.track_type == "Video"]
    return (
        (video_tracks[0].width, video_tracks[0].height)
        if len(video_tracks) >= 1
        else (-1, -1)
    )


def video_encode_for_mobile(src_file: str, tgt_file: str, target_height=480) -> None:
    i_w, i_h = find_video_dims(src_file)
    o_w, o_h = (target_height, target_height)
    crop_w = 0
    crop_h = 0
    if i_w > i_h:
        # for now assumes we want to zoon in slighly on landscape videos
        # before cropping to square
        crop_h = i_h * 0.25
        crop_w = i_w - (i_h - crop_h)
    else:
        crop_h = crop_h - crop_h
    os.makedirs(os.path.dirname(tgt_file), exist_ok=True)
    output_command = [
        "-y",
        "-filter:v",
        f"crop=iw-{crop_w:.0f}:ih-{crop_h:.0f},scale={o_w:.0f}:{o_h:.0f}",
        "-c:v",
        "libx264",
        "-crf",
        "23",
        "-pix_fmt",
        "yuv420p",
        "-movflags",
        "+faststart",
        "-c:a",
        "aac",
        "-ac",
        "1",
        "-loglevel",
        "quiet",
    ]
    ff = ffmpy.FFmpeg(
        inputs={src_file: None}, outputs={tgt_file: tuple(i for i in output_command)}
    )
    ff.run()


def video_encode_for_web(
    src_file: str, tgt_file: str, max_height=720, target_aspect=1.77777777778
) -> None:
    i_w, i_h = find_video_dims(src_file)
    crop_w = 0
    crop_h = 0
    o_w = 0
    o_h = 0
    i_aspect = float(i_w) / float(i_h)
    if i_aspect >= target_aspect:
        crop_w = i_w - (i_h * target_aspect)
        o_h = round(min(max_height, i_h))
    else:
        crop_h = i_h - (i_w * (1.0 / target_aspect))
        o_h = round(min(max_height, i_w * (1.0 / target_aspect)))
    o_w = int(o_h * target_aspect)
    os.makedirs(os.path.dirname(tgt_file), exist_ok=True)
    output_command = [
        "-y",
        "-filter:v",
        f"crop=iw-{crop_w:.0f}:ih-{crop_h:.0f},scale={o_w:.0f}:{o_h:.0f}",
        "-c:v",
        "libx264",
        "-crf",
        "23",
        "-pix_fmt",
        "yuv420p",
        "-movflags",
        "+faststart",
        "-c:a",
        "aac",
        "-ac",
        "1",
        "-loglevel",
        "quiet",
    ]
    ff = ffmpy.FFmpeg(
        inputs={src_file: None}, outputs={tgt_file: tuple(i for i in output_command)}
    )
    ff.run()


def slice_audio(
    src_file: str, target_file: str, time_start: float, time_end: float
) -> None:
    output_command = [
        "-y",
        "-ss",
        f"{time_start}",
        "-to",
        f"{time_end}",
        "-ac",
        "1",
        "-q:a",
        "5",
        "-loglevel",
        "quiet",
    ]
    if target_file.endswith(".mp3"):
        output_command.extend(["-acodec", "libmp3lame"])
    os.makedirs(os.path.dirname(target_file), exist_ok=True)
    ff = ffmpy.FFmpeg(
        inputs={src_file: None}, outputs={target_file: tuple(i for i in output_command)}
    )
    ff.run()


def slice_video(
    src_file: str,
    target_file: str,
    time_start: float,
    time_end: float,
    normalize_audio: bool = True,
    normalize_audio_lrt: int = 7,
) -> None:
    os.makedirs(os.path.dirname(target_file), exist_ok=True)
    output_command = [
        "-y",
        "-ss",
        f"{time_start}",
        "-to",
        f"{time_end}",
        "-c:v",
        "libx264",
        "-crf",
        "23",
        "-pix_fmt",
        "yuv420p",
        "-movflags",
        "+faststart",
        "-c:a",
        "aac",
        "-ac",
        "1",
        "-loglevel",
        "quiet",
    ]
    ff = ffmpy.FFmpeg(
        inputs={src_file: None}, outputs={target_file: tuple(i for i in output_command)}
    )
    ff.run()
    if normalize_audio:
        fbase, fext = os.path.splitext(target_file)
        tmp_file = os.path.join(fbase, f".tmp{fext}")
        subprocess.run(
            [
                "ffmpeg-normalize",
                target_file,
                "--output",
                tmp_file,
                "-lrt",
                "7",
                "-v",
                "-c:a",
                "aac",
                "-c:v",
                "libx264",
                "-ext",
                "mp4",
                "--extra-output-options",
                f"-y -crf 23 -pix_fmt yuv420p -movflags +faststart -loglevel quiet",
            ]
        )
        os.replace(tmp_file, target_file)


def video_to_audio(input_file, output_file=None, output_audio_encoding="mp3"):
    """
    Converts the .mp4 file to an audio file (.mp3 by default).
    Later, this audio file is split into smaller chunks for each Q-A pair.
    This is done because we want transcriptions for each question and the interview contains
    lots of other content like general talking and discussions.
    We use the timestamps for each Q-A to split the .ogg file.
    This function is equivalent to running `ffmpeg -i input_file output_file -loglevel quiet` on the command line.

    Parameters:
    input_file: Examples are /example/path/to/session1/session1part1.mp4, /example/path/to/session1/session1part2.mp4
    output_file: if not set, uses {input_file}.mp3

    Returns:
    error_code: if conversion fails, return 1
    """
    error_code = 0
    if os.path.exists(input_file):
        input_ext = os.path.splitext(input_file)[1]
        output_file = output_file or re.sub(
            f".{input_ext}$", f".{output_audio_encoding}", input_file
        )
        output_command = "-loglevel quiet -y"
        ff = ffmpy.FFmpeg(
            inputs={input_file: None}, outputs={output_file: output_command}
        )
        ff.run()
    else:
        print("ERROR: Can't covert audio, {} doesn't exist".format(input_file))
        error_code = 1
    return error_code
