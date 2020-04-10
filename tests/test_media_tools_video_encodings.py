import pytest
from unittest.mock import Mock, patch

from callee.operators import Contains

from mentor_pipeline.media_tools import video_encode_for_mobile, video_encode_for_web

from .helpers import Bunch


@patch("os.makedirs")
@patch("pymediainfo.MediaInfo.parse")
@patch("ffmpy.FFmpeg")
@pytest.mark.parametrize(
    "input_video_dims,expected_filter",
    [
        ((1024, 640), "iw-544:ih-160,scale=480:480"),
        ((1280, 720), "iw-740:ih-180,scale=480:480"),
        ((1920, 1080), "iw-1110:ih-270,scale=480:480"),
    ],
)
def test_video_encode_for_mobile_outputs_480x480_video(
    mock_ffmpeg_cls,
    mock_media_info_parse,
    mock_makedirs,
    input_video_dims,
    expected_filter,
):
    # TODO: update test to support a wider range of arbitrary input video sizes?
    input = "some_input_video.mp4"
    output = "output_video_path.mp4"
    mock_media_info_parseResult = Bunch(
        tracks=[
            Bunch(
                track_type="Video",
                width=input_video_dims[0],
                height=input_video_dims[1],
            )
        ]
    )
    mock_media_info_parse.return_value = mock_media_info_parseResult
    mockFFmpegInst = Mock()
    mock_ffmpeg_cls.return_value = mockFFmpegInst
    video_encode_for_mobile(input, output)
    mock_ffmpeg_cls.assert_called_once_with(
        inputs={input: None}, outputs={output: Contains(f"crop={expected_filter}")}
    )
    mockFFmpegInst.run.assert_called_once()


@patch("os.makedirs")
@patch("pymediainfo.MediaInfo.parse")
@patch("ffmpy.FFmpeg")
@pytest.mark.parametrize(
    "input_video_dims,expected_filter",
    [
        ((1024, 640), "iw-0:ih-64,scale=1024:576"),
        ((1280, 720), "iw-0:ih-0,scale=1280:720"),
        ((1920, 1080), "iw-0:ih-0,scale=1280:720"),
    ],
)
def test_video_encode_for_web_outputs_16x9_video_max_720p(
    mock_ffmpeg_cls,
    mock_media_info_parse,
    mock_makedirs,
    input_video_dims,
    expected_filter,
):
    input = "some_input_video.mp4"
    output = "output_video_path.mp4"
    mock_media_info_parseResult = Bunch(
        tracks=[
            Bunch(
                track_type="Video",
                width=input_video_dims[0],
                height=input_video_dims[1],
            )
        ]
    )
    mock_media_info_parse.return_value = mock_media_info_parseResult
    mockFFmpegInst = Mock()
    mock_ffmpeg_cls.return_value = mockFFmpegInst
    video_encode_for_web(input, output)
    mock_ffmpeg_cls.assert_called_once_with(
        inputs={input: None}, outputs={output: Contains(f"crop={expected_filter}")}
    )
    mockFFmpegInst.run.assert_called_once()
